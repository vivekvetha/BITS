#!/usr/bin/env bash
set -euo pipefail
##########################################################################
######
# AWS Billing Seed Script (CLI-only, one-file)
# - Creates IAM role for Lambda logging
# - Creates a Lambda that sleeps (to generate metered duration)
# - Tags Lambda with Team/Project/Feature
# - Optionally creates & tags one S3 bucket, does a tiny PUT/GET
# - Optional cleanup of all created resources
#
# HOW TO RUN (default: Team1/Project1/Feature1, sleep=90s, S3 enabled, cleanup ON):
# chmod +x aws_billing_seed.sh
# ./aws_billing_seed.sh
#
# EXAMPLES:
# TEAM="Team3" PROJECT="Project3" FEATURE="Feature3" ./aws_billing_seed.sh
# SLEEP_SECONDS=120 DO_S3=false ./aws_billing_seed.sh
# KEEP_RESOURCES=true ./aws_billing_seed.sh
#
# AFTER RUN:
# - Check CloudWatch Logs immediately for Lambda execution.
# - Check Cost Explorer & Billing Home after ~24 hours.
# - In Billing -> Cost allocation tags, activate Team/Project/Feature if first time.
##########################################################################

############################
# Configuration (edit or pass as env vars)
############################
REGION="${REGION:-${AWS_REGION:-ap-south-1}}"

# Tag values for cost allocation
TEAM="${TEAM:-Team3}"
PROJECT="${PROJECT:-Project3}"
FEATURE="${FEATURE:-Feature3}"
ENVIRONMENT_TAG="${ENVIRONMENT_TAG:-Lab}"
# Lambda execution settings
SLEEP_SECONDS="${SLEEP_SECONDS:-90}" # 60..120 recommended (or leave as 90)
LAMBDA_MEMORY_MB="${LAMBDA_MEMORY_MB:-128}"
LAMBDA_TIMEOUT_SEC="${LAMBDA_TIMEOUT_SEC:-180}"
# S3 behavior (true/false). S3 cost allocation is based on BUCKET tags.
DO_S3="${DO_S3:-true}"
# Cleanup behavior: if true, the script will remove all created resources at end
KEEP_RESOURCES="${KEEP_RESOURCES:-false}"
# Resource names
ROLE_NAME="${ROLE_NAME:-billing-seed-role}"
FUNC_NAME="${FUNC_NAME:-billing-seed-lambda}"
ZIP_FILE="${ZIP_FILE:-lambda_seed.zip}"
BUCKET_NAME="${BUCKET_NAME:-billing-seed-bkt-$RANDOM$RANDOM}"

############################
# Helpers
############################
log() { printf "\n[%s] %s\n" "$(date '+%H:%M:%S')" "$*"; }
die() { printf "\nERROR: %s\n" "$*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "Missing dependency: $1"; }

############################
# Pre-flight checks
############################
need aws
need zip

export AWS_PAGER=""
log "Region: $REGION"
log "Tags : Team=$TEAM, Project=$PROJECT, Feature=$FEATURE,
Environment=$ENVIRONMENT_TAG"
log "Lambda: sleep=${SLEEP_SECONDS}s, memory=${LAMBDA_MEMORY_MB}MB,
timeout=${LAMBDA_TIMEOUT_SEC}s"
log "S3 : DO_S3=$DO_S3, bucket=$BUCKET_NAME"
log "Clean : KEEP_RESOURCES=$KEEP_RESOURCES"


############################
# 1) Create minimal IAM role for Lambda logs
############################
log "Creating IAM role: $ROLE_NAME (if not exists)"

cat > trust_policy.json <<'EOF'
{
"Version": "2012-10-17",
"Statement": [
 { "Effect": "Allow",
 "Principal": { "Service": "lambda.amazonaws.com" },
 "Action": "sts:AssumeRole"
 }
]
}
EOF
aws iam create-role \
--role-name "$ROLE_NAME" \
--assume-role-policy-document file://trust_policy.json \
>/dev/null 2>&1 || true
aws iam attach-role-policy \
--role-name "$ROLE_NAME" \
--policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
>/dev/null 2>&1 || true
sleep 6
ROLE_ARN="$(aws iam get-role --role-name "$ROLE_NAME" --query 'Role.Arn' --output text
2>/dev/null || true)"
[ -n "$ROLE_ARN" ] || die "Unable to obtain role ARN for $ROLE_NAME"
log "Role ARN: $ROLE_ARN"


############################
# 2) Create Lambda function (sleep worker)
############################
log "Building Lambda package"
cat > lambda_function.py <<'EOF'
import time, json, random
def handler(event, context):
    try:
        s = int(event.get("sleep", 0)) if isinstance(event, dict) else 0
    except Exception as e:
        print(f"Error: {e}")
        s = 0
    if s <= 0:
        s = random.randint(60, 120)
    time.sleep(s)
    return {"slept_seconds": s}
EOF
zip -q "$ZIP_FILE" lambda_function.py
log "Creating Lambda function: $FUNC_NAME"
aws lambda create-function \
--function-name "$FUNC_NAME" \
--runtime python3.12 \
--handler lambda_function.handler \
--role "$ROLE_ARN" \
--memory-size "$LAMBDA_MEMORY_MB" \
--timeout "$LAMBDA_TIMEOUT_SEC" \
--zip-file "fileb://$ZIP_FILE" \
--region "$REGION" \
>/dev/null 2>&1 || true


# Wait until Active
for _ in $(seq 1 30); do
STATE="$(aws lambda get-function-configuration --function-name "$FUNC_NAME" \
 --region "$REGION" --query 'State' --output text 2>/dev/null || echo "")"
[ "$STATE" = "Active" ] && break
sleep 2
done
[ "$STATE" = "Active" ] || die "Lambda $FUNC_NAME did not reach Active state."
log "Lambda state: $STATE"


#######################
# 3) Tag Lambda (Team/Project/Feature/Environment)
############################
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
FUNC_ARN="arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:${FUNC_NAME}"
log "Tagging Lambda with cost allocation tags"
aws lambda tag-resource \
--resource "$FUNC_ARN" \
--tags "Team=$TEAM","Project=$PROJECT","Feature=$FEATURE","Environment=$ENVIRONMENT_TAG" \
--region "$REGION" \
>/dev/null


############################
# 4) Invoke Lambda once (real billed duration)
############################
log "Invoking Lambda for ${SLEEP_SECONDS}s"
aws lambda invoke \
  --function-name "$FUNC_NAME" \
  --invocation-type Event \
  --payload "{\"sleep\":$SLEEP_SECONDS}" \
  --cli-binary-format raw-in-base64-out \
  --region "$REGION" \
  out.json >/dev/null
log "Invoke requested. Check CloudWatch Logs to confirm execution."

############################
# 5) (Optional) Create tagged S3 bucket + tiny PUT/GET
############################
if [ "$DO_S3" = "true" ]; then
log "Creating S3 bucket: $BUCKET_NAME"
aws s3api create-bucket \
 --bucket "$BUCKET_NAME" \
 --create-bucket-configuration "LocationConstraint=$REGION" \
 --region "$REGION" \
 >/dev/null
log "Tagging S3 bucket for cost allocation"
aws s3api put-bucket-tagging \
 --bucket "$BUCKET_NAME" \
 --tagging "TagSet=[{Key=Team,Value=${TEAM}},{Key=Project,Value=${PROJECT}},{Key=Feature,Value=${FEATURE}},{Key=Environment,Value=${ENVIRONMENT_TAG}}]" \
 --region "$REGION" \
 >/dev/null

log "S3 PUT/GET small object"
echo "hello-$RANDOM" > hello.txt
aws s3 cp hello.txt "s3://${BUCKET_NAME}/hello.txt" --region "$REGION" >/dev/null
aws s3 cp "s3://${BUCKET_NAME}/hello.txt" ./downloaded.txt --region "$REGION" >/dev/null
fi
############################
# Summary & guidance
############################
log "DONE: Generated real, tagged usage."
echo " Lambda : $FUNC_NAME (ARN: $FUNC_ARN)"
if [ "$DO_S3" = "true" ]; then
echo " S3 bucket: $BUCKET_NAME"
fi
echo " Tags : Team=$TEAM, Project=$PROJECT, Feature=$FEATURE,
Environment=$ENVIRONMENT_TAG"
echo
echo "NEXT STEPS:"
echo " - In Billing → Cost allocation tags: activate Team/Project/Feature if first time."
echo " - Wait ~24h, then in Cost Explorer: Group by Tag:Team (and secondary:
Project/Feature)."
echo " - Billing Home widgets (Cost summary, breakdown, trends) will reflect CE data."

############################
# 6) Cleanup (optional)
############################
if [ "$KEEP_RESOURCES" = "true" ]; then
log "KEEP_RESOURCES=true -> Skipping cleanup. Remember to delete resources later."
exit 0
fi
log "Cleaning up resources..."
# Delete Lambda
aws lambda delete-function \
--function-name "$FUNC_NAME" \
--region "$REGION" \
>/dev/null 2>&1 || true

# Detach policy & delete role
aws iam detach-role-policy \
--role-name "$ROLE_NAME" \
--policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
>/dev/null 2>&1 || true
aws iam delete-role \
--role-name "$ROLE_NAME" \
>/dev/null 2>&1 || true
# Empty & delete bucket if we created it
if [ "$DO_S3" = "true" ]; then
aws s3 rm "s3://${BUCKET_NAME}" --recursive --region "$REGION" >/dev/null 2>&1 || true
aws s3api delete-bucket --bucket "$BUCKET_NAME" --region "$REGION" >/dev/null 2>&1 ||
true
fi
# Local files
rm -f trust_policy.json lambda_function.py "$ZIP_FILE" hello.txt downloaded.txt out.json
log "Cleanup complete."
