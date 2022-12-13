import argparse
import json
import os
import yaml
import logging

from google.cloud import aiplatform

logger = logging.getLogger()
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logger.setLevel(log_level)

SERVICE_ACCOUNT = ''

def run_pipeline(
    project_id: str,
    pipeline_root: str,
    parameter_values_path: str,
    pipeline_spec_path: str,
    display_name: str = 'mlops-pipeline-run',
    enable_caching: bool = False):
    """Executes a pipeline run.
    Args:
      project_id: The project_id.
      pipeline_root: GCS location of the pipeline runs metadata.
      parameter_values_path: Location of parameter values JSON.
      pipeline_spec_path: Location of the pipeline spec JSON.
      display_name: Name to call the pipeline.
      enable_caching: Should caching be enabled (Boolean)
    """
    with open(parameter_values_path, 'r') as file:
      try:
          pipeline_params = json.load(file)
      except ValueError as exc:
          print(exc)
    logging.debug('Pipeline Parms Configured:')
    logging.debug(pipeline_params)

    aiplatform.init(project=project_id)
    job = aiplatform.PipelineJob(
      display_name = display_name,
      template_path = pipeline_spec_path,
      pipeline_root = pipeline_root,
      parameter_values = pipeline_params,
      enable_caching = enable_caching
    )
    logging.debug('AI Platform job built. Submitting...')
    #job.submit(service_account=SERVICE_ACCOUNT)
    job.submit()
    logging.debug('Job sent!')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str,
                        help='The config file for setting default values.')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as config_file:
      config = yaml.load(config_file, Loader=yaml.FullLoader)

    run_pipeline(project_id=config['gcp']['project_id'],
                 pipeline_root=config['pipelines']['pipeline_storage_path'],
                 parameter_values_path=config['pipelines']['parameter_values_path'],
                 pipeline_spec_path=config['pipelines']['pipeline_job_spec_path']) 
