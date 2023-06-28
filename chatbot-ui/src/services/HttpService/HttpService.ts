import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';

import { AuthService } from '../AuthService';

const _axios: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_CHAT_SERVICE_URL,
});


const handleSuccess = (response: any) => response;

const handleError = (error: any) => {
  if(error?.response?.status === 401) {
    AuthService.doLogout();
  }
  return Promise.reject(error);

}

_axios.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  // eslint-disable-next-line no-param-reassign
  config.headers.Authorization = `Bearer ${AuthService.getToken()}`;
  config.headers['Content-Type'] = 'application/json';
  config.headers['Access-Control-Allow-Origin'] = '*';
  return config;
});

_axios.interceptors.response.use(handleSuccess, handleError);

export const fetchPrompt = (message: string, conversationId: string | null , isOverride: boolean , modelName: string | undefined) => fetch(`${import.meta.env.VITE_CHAT_SERVICE_URL}/completions`, { method: "POST", headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${AuthService.getToken()}` }, body: JSON.stringify(conversationId ? {message: message, conversation_id: conversationId , isOverride: isOverride, model_name : modelName}  : { message: message })});

export const analyzeMessage = (message: string) => {
  return _axios.post('/analyze', { message: message });
};

export const anonymizeMessage = (message: string) => {
  return _axios.post('/anonymize', { message: message });
}
export const archiveConversations = () => {
  return _axios.delete('/conversations/archive');
}

export const archiveUnarchiveConversation = (conversationId: string, isArchived: boolean) => {
  return _axios.delete(`/conversations/archive/${conversationId}?flag=${isArchived}`);
}

export const fetchAllConversations = (getArchived:boolean) => {
  return _axios.get(`/conversations?archived=${getArchived}`);
}

export const fetchConversationById = (id:string) => {
  return _axios.get(`/conversations/${id}`);
}

//folders and prompts

export const fetchFolders = () => {
  return _axios.get('/folders');
}

export const updateUserFolders = (folders: any) => {
  return _axios.put('/folders', folders);
}

export const fetchPrompts = () => {
  return _axios.get('/prompts');
}

export const updateUserPrompts = (prompts: any) => {
  return _axios.put('/prompts', prompts);
}

export const updateConversationProperties = (conversationId: string, title: string , folderId: string|null) => {
return _axios.put(`/conversations/${conversationId}/properties`, {title: title, folderId: folderId});
}

export const requestApproval = (conversationId: string) => {
  return _axios.get(`/requestapproval/${conversationId}`);
}