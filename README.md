This is still in the Alpha stage.

## PrimeHub Job

Submit PrimeHub jobs easier

### Install

```
pip install primehub_job
```

### How to Use

1. PrimeHub version >= 2.8
2. Set the API_TOKEN environment variable
3. Make sure your group have group volume

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

### Restrictions

1. Don't use global variables in functions
2. If you want to return a model, please use the framework's saver to save model, and return the saved model path to load the model. Here is the example:
```python
# tensorflow
def export_model(model, export_path):
    if os.path.isdir(export_path):
        print('Cleaning up\n')
        shutil.rmtree(export_path)

    model.save(export_path)
    return export_path

@submit_phjob()
def training(epochs=2, dropout=0.2):
    mnist = tf.keras.datasets.mnist

    (x_train, y_train),(x_test, y_test) = mnist.load_data()
    x_train, x_test = x_train / 255.0, x_test / 255.0

    model = tf.keras.models.Sequential([
      tf.keras.layers.Flatten(input_shape=(28, 28)),
      tf.keras.layers.Dense(512, activation=tf.nn.relu),
      tf.keras.layers.Dropout(dropout),
      tf.keras.layers.Dense(10, activation=tf.nn.softmax)
    ])

    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    model.fit(x_train, y_train, epochs=epochs)
    model.evaluate(x_test, y_test)

    return export_model(model, '1')

job_id = training()

# load trained model
model = tf.keras.models.load_model(get_phjob_folder_path(job_id) + '/' + wait_and_get_phjob_result(job_id))
``` 

### Run the Tests

```
python -m pytest
```