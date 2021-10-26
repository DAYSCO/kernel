import os
import sys
from flask_api import FlaskAPI
from .routes import app_bp


app = FlaskAPI(__name__)
app.register_blueprint(app_bp)


if not os.environ.get('TESTING', 'FALSE') == 'TRUE':
    from opentelemetry import trace
    from opentelemetry.instrumentation.flask import FlaskInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        ConsoleSpanExporter,
        SimpleSpanProcessor,
    )

    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

    FlaskInstrumentor().instrument_app(app)
    RequestsInstrumentor().instrument()

    tracer = trace.get_tracer(__name__)
    tracer.start_as_current_span('app-request')
