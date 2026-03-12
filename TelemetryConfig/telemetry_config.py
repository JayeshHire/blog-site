from opentelemetry import trace, metrics
from prometheus_client import start_http_server
from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
import logging
from pydantic import BaseModel

# Service name is required for most backends
# resource = Resource.create(attributes={
#     SERVICE_NAME: "your-service-name"
# })

# Start Prometheus client
# start_http_server(port=9464, addr="localhost")

# Initialize PrometheusMetricReader which pulls metrics from the SDK
# on-demand to respond to scrape requests
# reader = PrometheusMetricReader()
# provider = MeterProvider(resource=resource, metric_readers=[reader])
# metrics.set_meter_provider(provider)

# initializing traces
tracer = trace.get_tracer("")

# initializing logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("blog-site")


# basemodel for storing origination data 
# for the span from inside the code.
class Origination(BaseModel):
    package: str 
    module: str 
    func_name: str 

def origination_(package: str, module: str, func_name: str):
    o = Origination(package=package, 
                    module=module, 
                    func_name=func_name)
    return o.model_dump()
