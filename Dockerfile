FROM python:3.9.8-slim-bullseye as base-image

# Update system packages
COPY scripts/install-base-packages.sh .
RUN ./install-base-packages.sh && rm ./install-base-packages.sh

FROM base-image AS runtime-image

COPY . /workdir
WORKDIR /workdir
RUN pip install --no-cache-dir .

CMD ["ltd-mason-travis"]
