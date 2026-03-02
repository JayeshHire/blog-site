
**Install opentelemetry exporter for otlp and prometheus**

```bash
pip install opentelemetry-exporter-prometheus
```

```bash
pip install opentelemetry-exporter-otlp
```



**Running Jaegar inside a container**

```bash
docker run --rm \
  -e COLLECTOR_ZIPKIN_HOST_PORT=:9411 \
  -p 16686:16686 \
  -p 4317:4317 \
  -p 4318:4318 \
  -p 9411:9411 \
  jaegertracing/all-in-one:latest
```

**Running prometheus inside a container**

```bash
docker run --rm -v ${PWD}/prometheus.yml:/prometheus/prometheus.yml -p 9090:9090 prom/prometheus --web.enable-otlp-receiver
```

