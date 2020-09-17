import { URLExt } from '@jupyterlab/coreutils';
import { ReadonlyJSONObject } from '@lumino/coreutils';
import { ServerConnection } from '@jupyterlab/services';


/**
 * Call the API extension
 *
 * @param endPoint API REST end point for the extension; default ''
 * @param method HTML method; default 'GET'
 * @param body JSON object to be passed as body or null; default null
 * @param namespace API namespace; default 'jupyterlab-primehub'
 * @returns The response body interpreted as JSON
 */
export async function requestAPI<T>(
  endPoint = '',
  method = 'GET',
  body: ReadonlyJSONObject | null = null,
  namespace = 'jupyterlab-primehub'
): Promise<T> {
  // Make request to Jupyter API
  const settings = ServerConnection.makeSettings();
  const requestUrl = URLExt.join(
    settings.baseUrl,
    namespace, // API Namespace
    endPoint
  );

  const init: RequestInit = {
    method,
    body: body ? JSON.stringify(body) : undefined
  };

  let response: Response;
  try {
    response = await ServerConnection.makeRequest(requestUrl, init, settings);
  } catch (error) {
    throw new ServerConnection.NetworkError(error);
  }

  let data: any = await response.text();
  if (data.length > 0) {
    try {
      data = JSON.parse(data);
    } catch (error) {
      console.log('Not a JSON response body.', response);
    }
  }

  if (!response.ok) {
    throw new ServerConnection.ResponseError(response, data.message || data);
  }

  return data;
}