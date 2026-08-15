FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY hermes ./hermes
COPY boards ./boards
COPY firmware ./firmware
RUN pip install --no-cache-dir -e .
EXPOSE 8790
CMD ["bringup", "serve", "--host", "0.0.0.0", "--port", "8790"]
