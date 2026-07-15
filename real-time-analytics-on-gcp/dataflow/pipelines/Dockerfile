# Flex Template image for the streaming pipeline. Built and pushed by
# scripts/deploy_dataflow_pipeline.sh to the Artifact Registry repo
# Terraform provisions (infra/terraform/modules/dataflow).
FROM gcr.io/dataflow-templates-base/python311-template-launcher-base

ARG WORKDIR=/template
WORKDIR ${WORKDIR}

# Preserve the same relative layout as the repo (dataflow/ next to common/)
# so the sys.path.insert(parents[N]) resolution in the transform modules
# resolves identically inside the container as it does when run locally.
COPY dataflow/pipelines/ ${WORKDIR}/dataflow/pipelines/
COPY dataflow/transforms/ ${WORKDIR}/dataflow/transforms/
COPY common/ ${WORKDIR}/common/

ENV FLEX_TEMPLATE_PYTHON_PY_FILE="${WORKDIR}/dataflow/pipelines/streaming_pipeline.py"
ENV FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE="${WORKDIR}/dataflow/pipelines/requirements.txt"
ENV PYTHONPATH="${WORKDIR}"

RUN pip install --no-cache-dir --upgrade pip \
    # requirements.txt's `-e ../../common` is relative to its ORIGINAL
    # location in the repo, which no longer applies once copied into the
    # image — install everything else from it, then install common
    # explicitly by its real in-image path.
    && grep -v '^-e' ${WORKDIR}/dataflow/pipelines/requirements.txt > /tmp/requirements-no-editable.txt \
    && pip install --no-cache-dir -r /tmp/requirements-no-editable.txt \
    && pip install --no-cache-dir -e ${WORKDIR}/common
