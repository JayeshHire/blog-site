
-- install the necessary packages for opentelemetry python sdk, api and other tools like `opentelemetry-instrument` and `opentelemetry-bootstrap`. The `opentelemetry-distro` package contains all the above. Install `opentelemetry-distro` using the following command.

`pip install opentelemetry-distro`

-- To automatically install all the instrumentation for the libraries which are installed in your environment run the following command. The following command will install the necessary packages for instrumentation of all the supported libraries in your application if that instrumentation exists for that library.

`opentelemetry-bootstrap -a install`

## Set the environment variables.

-- enable the opentelemetry auto instrumentation for python

`$env:OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED="true"`

-- set the service name

`$env:OTEL_SERVICE_NAME="blog-site"`

-- set the exporters for traces, metrics and logs. 
Since for now we just need to add traces to the application. We'll just set the environment variables for traces. But the other environment variables will be needed so I am just noting them here for now.

`$env:OTEL_EXPORTER_TRACES_ENDPOINT="127.0.0.1:4317"`

`$env:OTEL_EXPORTER_TRACES_PROTOCOL="otlp"`

`$env:OTEL_EXPORTER_METRICS_ENDPOINT="127.0.0.1:9464"`

`$env:OTEL_EXPORTER_METRICS_PROTOCOL="http/protobuf"`

`$env:OTEL_EXPORTER_LOGS_ENDPOINT="console"`

## Run the instrumented app.

`opentelemetry-instrument uvicorn main:app`


## Exporter backend setup

-- Setting up jaeger for collecting traces by running it inside a docker container.

```bash
docker run --rm \
  -e COLLECTOR_ZIPKIN_HOST_PORT=:9411 \
  -p 16686:16686 \
  -p 4317:4317 \
  -p 4318:4318 \
  -p 9411:9411 \
  jaegertracing/all-in-one:latest
```

```powershell
docker run --rm `
  -e COLLECTOR_ZIPKIN_HOST_PORT=:9411 `
  -p 16686:16686 `
  -p 4317:4317 `
  -p 4318:4318 `
  -p 9411:9411 `
  jaegertracing/all-in-one:latest
```