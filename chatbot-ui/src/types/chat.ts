
export interface Message {
  role: Role;
  content: string;
  userActionRequired: boolean;
  msg_info: any
}

export type Role = 'assistant' | 'user' | 'guardrails';

export interface ChatBody {
  messages: Message[];
  key: string;
  prompt: string;
  temperature: number;
 
}



export interface Conversation {
  model: string;
  id: string;
  title: string;
  messages: Message[];
  prompt: string;
  temperature: number;
  folderId: string | null;
  archived: boolean;
}
