import { IconBolt, IconBook } from '@tabler/icons-react'; 

export interface Tile {
    displayName: string;
    icon: JSX.Element;
    task: string;
  }
  
export const TilesList: Tile[] = [
  {
    displayName: 'Conversational Chatbot',
    icon: <IconBolt size={80} />,
    task: 'conversation',
  },
  {
    displayName: 'Knowledge Mining on Private Doc',
    icon: <IconBook size={80} />,
    task: 'qa-retreival'
  }
];
