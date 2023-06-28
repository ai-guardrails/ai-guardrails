import axios, { AxiosInstance, InternalAxiosRequestConfig } from "axios";

import { AuthService } from "../AuthService";

const _axios: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_CHAT_SERVICE_URL,
});

const handleSuccess = (response: any) => response;

const handleError = (error: any) => {
  if (error?.response?.status === 401) {
    AuthService.doLogout();
  }
  return Promise.reject(error);
};

_axios.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  // eslint-disable-next-line no-param-reassign
  config.headers.Authorization = `Bearer ${AuthService.getToken()}`;
  config.headers["Content-Type"] = "application/json";
  config.headers["Access-Control-Allow-Origin"] = "*";
  return config;
});

_axios.interceptors.response.use(handleSuccess, handleError);

export const fetchGuestToken = () => {
  return _axios.get("/fetchguesttoken");
};

export const getGridData = (entity: string,params: any) => {
  const stringParams = Object.keys(params)
    .map((key, index) => `${key}=${JSON.stringify(params[key])}`)
    .join("&");
  return _axios.get(`/${entity}?${stringParams}`);
};

export const updateGridData = (entity: string, id: any, data: any) => {
  return _axios.put(`/${entity}/${id}`, data);
}

export const approveEscalation = ( conversationId:string, user_email:string ) => {
  return _axios.put(`/approve_escalation/${conversationId}`, user_email);
}

export const rejectEscalation = ( conversationId:string, user_email:string ) => {
  return _axios.put(`/reject_escalation/${conversationId}`, user_email);
}
