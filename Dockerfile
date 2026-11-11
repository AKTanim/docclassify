# AWS's official image for Python 3.13 Lambda functions.
FROM public.ecr.aws/lambda/python:3.13

# Install the runtime packages first, so Docker can reuse this layer
# when only the code changes.
# Usage: uv export --no-dev --no-emit-project --format requirements-txt -o requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# The code and the mock store's documents.
COPY src/docclassify ${LAMBDA_TASK_ROOT}/docclassify
# The following two lines go away for a real store
COPY sample_docs ${LAMBDA_TASK_ROOT}/sample_docs
ENV DOCUMENT_STORE_DIR=/var/task/sample_docs

# The function Lambda calls: module docclassify.handler, function lambda_handler.
CMD ["docclassify.handler.lambda_handler"]
