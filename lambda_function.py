import json
import boto3
import time
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
def lambda_handler(event, context):
    codepipeline = boto3.client('codepipeline')
    ts = int(time.time())
    try:
        cfnid= str(event['CodePipeline.job']['data']['actionConfiguration']['configuration']['UserParameters'])
        cloudfront = boto3.client('cloudfront')
        response_cloudfront = cloudfront.create_invalidation(
            DistributionId=cfnid,
            InvalidationBatch={
                'Paths': {
                    'Quantity': 1,
                    'Items': [
                    '/*',
                    ]
                },
                'CallerReference': str(ts)
            }
        )
        logger.info(response_cloudfront)
        response_codepipeline = codepipeline.put_job_success_result(
            jobId=str(event['CodePipeline.job']['id']),
            currentRevision={
                'revision': str(event['CodePipeline.job']['data']['inputArtifacts'][0]['revision']),
                'changeIdentifier': str(ts)
            }
        )
        logger.info(response_codepipeline)
    except Exception as e:
        logger.error('Invalidation failed due to error:' + str(e))
        response = codepipeline.put_job_failure_result(
            jobId=str(event['CodePipeline.job']['id']),
            failureDetails={
                'type': 'JobFailed',
                'message': 'JobFailed due to exception:' + str(e),
                'externalExecutionId': str(ts)
            }
        )
        logger.info(response)
        raise

    return {
        'statusCode': 200,
        'body': 'Function has run',
        'timestamp': ts,
    }
