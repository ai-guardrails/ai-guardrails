import { KeyValuePair } from './data';

export interface Plugin {
  id: PluginID;
  name: PluginName;
  task:PluginTask;
  requiredKeys: KeyValuePair[];
}

export interface PluginKey {
  pluginId: PluginID;
  requiredKeys: KeyValuePair[];
}

export enum PluginID {
  CONVERSATION = "gpt-3.5-turbo",
  QA_PRIVATE_DOCS = "private-docs",

}

export enum PluginName {
  CONVERSATION = "Conversational Chatbot",
  QA_PRIVATE_DOCS = "Knowledge Mining on Private Docs",

}

export enum PluginTask {
  CONVERSATION= "conversation",
  QA_PRIVATE_DOCS = "qa-on-private-docs",

}

export const Plugins: Record<PluginID, Plugin> = {
  [PluginID.CONVERSATION]: {
    id: PluginID.CONVERSATION,
    name: PluginName.CONVERSATION,
    task:PluginTask.CONVERSATION,
    requiredKeys: [
      {
        key: 'CHAT_GPT_API_KEY',
        value: '',
      },
      {
        key: 'CHAT_GPT_CSE_ID',
        value: '',
      },
    ],
  },
  [PluginID.QA_PRIVATE_DOCS]: {
    id: PluginID.QA_PRIVATE_DOCS,
    name: PluginName.QA_PRIVATE_DOCS,
    task:PluginTask.QA_PRIVATE_DOCS,
    requiredKeys: [
      {
        key: 'PRIVATE_DOCS_API_KEY',
        value: '',
      },
      {
        key: 'PRIVATE_DOCS_CSE_ID',
        value: '',
      },
    ],
  },
  
};

export const PluginList = Object.values(Plugins);
