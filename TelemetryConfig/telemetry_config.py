from opentelemetry import trace, metrics
from prometheus_client import start_http_server
from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

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


tracer = trace.get_tracer("")
