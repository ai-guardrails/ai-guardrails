import { IconBolt, IconBook, IconNotebook,IconDatabase } from '@tabler/icons-react'; 

export interface Tile {
    displayName: string;
    icon: JSX.Element;
    task: string;
    additionalInputs?: string[];
  }
  
export const TilesList: Tile[] = [
  {
    displayName: 'Conversational Chatbot',
    icon: <IconBolt size={50} />,
    task: 'conversation',
  },
  {
    displayName: 'Knowledge Mining on Private Doc',
    icon: <IconBook size={50} />,
    task: 'qa-retreival'
  },
  {
    displayName: 'Summarize Real Estate Development Brief',
    icon: <IconNotebook size={50} />,
    task: 'summarize-brief',
    additionalInputs: ['fileUpload']
  },
  {
    displayName: 'Q&A on SQL Database.',
    icon: <IconDatabase size={50} />,
    task: 'qa-sql'
  }
];
