This is still in the Pre-Alpha stage.

# PrimeHub Job

Submit PrimeHub jobs easier

## Install

```
pip install primehub_job
```

## How to Use

1. Set the API_TOKEN environment variable
2. Make sure your group have group volume

``` python
from primehub_job import submit_phjob, get_phjob_logs, get_phjob_result, wait_and_get_phjob_result

# You can write @submit_job() to use default settings.
@submit_phjob(name='submitJob', image='datascience-notebook', instance_type='cpu')
def test(a, b='b'):
    print(a)
    print(b)
    return a, b

# Submit a job and wait the result
wait_and_get_phjob_result(test('aaa', 'ccc'))

# Submit a job
job_id = test('aaa', 'ccc')
# Get the running logs
print(get_phjob_logs(job_id))
# Get the job result
get_phjob_result(job_id)

```