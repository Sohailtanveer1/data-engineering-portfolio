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
# Point the RUNTIME requirements at the cleaned, editable-free file baked in
# below — NOT the repo's requirements.txt. The launcher re-runs
# `pip install -r` on this file at launch time from ${WORKDIR}, so a
# `-e ../../common` line here would resolve to /common (nonexistent) and
# kill the launch with "Failed to read the result file". common is installed
# separately by real in-image path in the RUN step instead.
ENV FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE="${WORKDIR}/requirements-runtime.txt"
ENV PYTHONPATH="${WORKDIR}"

RUN pip install --no-cache-dir --upgrade pip \
    # Strip the editable `-e ../../common` line into a persistent runtime
    # requirements file (everything else is a normal pinned package). This
    # file is what both the build below AND the launcher at runtime install.
    && grep -v '^-e' ${WORKDIR}/dataflow/pipelines/requirements.txt > ${WORKDIR}/requirements-runtime.txt \
    && pip install --no-cache-dir -r ${WORKDIR}/requirements-runtime.txt \
    # common is installed by its real in-image path; workers use this same
    # image, so supplychain_common is importable everywhere.
    && pip install --no-cache-dir -e ${WORKDIR}/common
