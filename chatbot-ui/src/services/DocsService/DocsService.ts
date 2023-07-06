import axios, { AxiosInstance, InternalAxiosRequestConfig } from "axios";

import { AuthService } from "../AuthService";

const _axios: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_DOCS_SERVICE_URL,
});

const handleSuccess = (response: any) => response;

const handleError = (error: any) => {
  if (error.response.status === 401) {
    AuthService.doLogout();
  }
  return Promise.reject(error);
};

_axios.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  // eslint-disable-next-line no-param-reassign
  config.headers.Authorization = `Bearer ${AuthService.getToken()}`;
  config.headers["Access-Control-Allow-Origin"] = "*";
  config.headers["Content-Type"] = "application/json";
  if(config.url=='/documents' && config.method=='post'){
    config.headers["Content-Type"] = "multipart/form-data";
  }
  return config;
});

_axios.interceptors.response.use(handleSuccess, handleError);


export const uploadDocuments = ( formData:FormData ) => {
  return _axios.post('/documents', formData);
}

export const getDocsGridData = (entity: string,params: any) => {
  const stringParams = Object.keys(params)
    .map((key, index) => `${key}=${JSON.stringify(params[key])}`)
    .join("&");
  return _axios.get(`/${entity}?${stringParams}`);
};

export const deleteDocsGridData = (id: number) => {
  return _axios.delete(`/documents/${id}`);
}
