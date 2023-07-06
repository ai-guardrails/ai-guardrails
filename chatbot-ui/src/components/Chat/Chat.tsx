import { IconClearAll, IconSettings, IconBolt, IconBook } from '@tabler/icons-react';
import {
  MutableRefObject,
  memo,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';
import toast from 'react-hot-toast';

// import { getEndpoint } from '@/utils/app/api';
import {
  updateConversation,
} from '@/utils/app/conversation';
import { throttle } from '@/utils/data/throttle';

import { ChatBody, Conversation, Message } from '@/types/chat';
import { Plugin } from '@/types/plugin';

import HomeContext from '@/pages/home/home.context';
import { PluginList } from '@/types/plugin';

import Spinner from '../Spinner';
import { ChatInput } from './ChatInput';
import { ChatLoader } from './ChatLoader';
import { ErrorMessageDiv } from './ErrorMessageDiv';
import { ModelSelect } from './ModelSelect';
import { SystemPrompt } from './SystemPrompt';
import { TemperatureSlider } from './Temperature';
import { MemoizedChatMessage } from './MemoizedChatMessage';
import { anonymizeMessage, fetchPrompt, requestApproval } from '@/services';
import PublicPrivateSwitch from '../PublicPrivateSwitch';


interface Props {
  stopConversationRef: MutableRefObject<boolean>;
}
const applicationName: string = import.meta.env.VITE_APPLICATION_NAME;

export const Chat = memo(({ stopConversationRef }: Props) => {
  function containsOnlyWhitespacesOrNewlines(str: string) {
    // Check if the string contains only whitespace characters or only newline characters
    return str.trim() === '' || str.split('').every(char => char === '\n' || char === '\r');
  }
  const {
    state: {
      selectedConversation,
      conversations,
      models,
      apiKey,
      pluginKeys,
      serverSideApiKeyIsSet,
      messageIsStreaming,
      modelError,
      loading,
      prompts,
      isPrivate
    },
    handleUpdateConversation,
    handleIsPrivate,
    dispatch: homeDispatch,
  } = useContext(HomeContext);

  const [currentMessage, setCurrentMessage] = useState<Message>();
  const [autoScrollEnabled, setAutoScrollEnabled] = useState<boolean>(true);
  const [showSettings, setShowSettings] = useState<boolean>(false);
  const [showScrollDownButton, setShowScrollDownButton] =
    useState<boolean>(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [plugin, setPlugin] = useState<Plugin>(PluginList[0]);


  const handleSend = useCallback(
    async (message: Message, deleteCount = 0, plugin: Plugin , isOverRide:boolean = false) => {
      if (containsOnlyWhitespacesOrNewlines(message.content)) return;
      message.content = message.content.trim();
      if(plugin.id === "gpt-3.5-turbo"){
        await anonymizeMessage(message.content)
        .then((res: any) => {
          message.content = res?.data?.result;
        })
        .catch((err) => {
          toast.error(err.message,{
            position:"bottom-right",
            duration:3000
          })
          console.log(err.message, "API ERROR");
        });
      }
      
      if (selectedConversation) {
        let updatedConversation: Conversation;
        if (deleteCount) {
          const updatedMessages = [...selectedConversation.messages];
          for (let i = 0; i < deleteCount; i++) {
            updatedMessages.pop();
          }
          updatedConversation = {
            ...selectedConversation,
            messages: [...updatedMessages, message],
          };
        } else {
          updatedConversation = {
            ...selectedConversation,
            messages: [...selectedConversation.messages, message],
          };
        }
        homeDispatch({
          field: 'selectedConversation',
          value: updatedConversation,
        });
        homeDispatch({ field: 'loading', value: true });
        homeDispatch({ field: 'messageIsStreaming', value: true });
        const chatBody: any = {
          message: message.content
        };

        let modelName = plugin?.id;
        let task=plugin?.task;
        const controller = new AbortController();
        let response: any;
        if(isOverRide){
          try{
            response = await fetchPrompt(
              updatedConversation.messages[updatedConversation.messages.length - 2].content,
              selectedConversation.id,
              isOverRide,
              modelName,
              task ,
              isPrivate
            );
          }
          catch(err:any){
            toast.error(err.message,{
              position:"bottom-right",
              duration:3000
            })
          }
        }else{
          try{
            response = await fetchPrompt(
              chatBody.message,
              selectedConversation.id,
              isOverRide,
              modelName,
              task,
              isPrivate
            );

          }catch(err:any){
            toast.error(err.message,{
              position:"bottom-right",
              duration:3000
            })
          }
        }

        if (!response.ok) {
          homeDispatch({ field: 'loading', value: false });
          homeDispatch({ field: 'messageIsStreaming', value: false });
          toast.error(response.statusText);
          return;
        }
        const data = response.body;
        if (!data) {
          homeDispatch({ field: 'loading', value: false });
          homeDispatch({ field: 'messageIsStreaming', value: false });
          return;
        }

          homeDispatch({ field: 'loading', value: false });
          const reader = data.getReader();
          const decoder = new TextDecoder("utf-8");
          let done = false;
          let isFirst = true;
          let text = '';
          let msg_info = null;
          let role;
          while (!done) {
            if (stopConversationRef.current === true) {
              controller.abort();
              done = true;
              break;
            }
            const { value, done: doneReading } = await reader.read();
            done = doneReading;
            const chunkValue = decoder.decode(value);
            let parsed;
            if(!chunkValue || chunkValue === '') continue;
            if(chunkValue.includes('}{')){
              var split = chunkValue.split('}{');
              for(var i = 0; i < split.length; i++){
                if(i === 0){
                  parsed = JSON.parse(split[i] + '}');
                }
                else if(i === split.length - 1){
                  parsed = JSON.parse('{' + split[i]);
                }
                else{
                  parsed = JSON.parse('{' + split[i] + '}');
                }

                if(parsed.content==undefined){
                  text='Sorry currently your request could not be fullfiled. Please try again.!';
                }
                else{

                  text += parsed.content;
                }
                msg_info = parsed.msg_info;
                role = parsed.role;
              }
            } else{
              parsed = JSON.parse(chunkValue);
              if(parsed.content==undefined){
                text='Sorry currently your request could not be fullfiled. Please try again.!';
              }
              else{
                text += parsed.content;
              }
              msg_info = parsed.msg_info;
              role = parsed.role;
              
            }
            if (isFirst) {
              isFirst = false;
              homeDispatch({ field: "refreshConversations", value: true });
              const updatedMessages: Message[] =
              updatedConversation.messages.map((message, index) => {
                  return {
                    ...message,
                    userActionRequired: false
                  };
              });
              if(isOverRide){
                updatedMessages.push({ role: 'guardrails', content: "You chose to Override the warning, proceeding to Open AI." ,msg_info:msg_info, userActionRequired: false})
              }
              updatedMessages.push({ role: role, content: text ,msg_info:msg_info, userActionRequired: parsed.user_action_required})
              updatedConversation = {
                ...updatedConversation,
                messages: updatedMessages,
              };
              console.log("updatedConversation",updatedConversation);
              homeDispatch({
                field: 'selectedConversation',
                value: updatedConversation,
              });
            } else {
              const updatedMessages: Message[] =
                updatedConversation.messages.map((message, index) => {
                  if (index === updatedConversation.messages.length - 1) {
                    return {
                      ...message,
                      content: text,
                    };
                  }
                  return message;
                });
              updatedConversation = {
                ...updatedConversation,
                messages: updatedMessages,
              };
              homeDispatch({
                field: 'selectedConversation',
                value: updatedConversation,
              });
            }
          }
          
          homeDispatch({ field: 'messageIsStreaming', value: false });
         
      }
    },
    [
      apiKey,
      conversations,
      pluginKeys,
      selectedConversation,
      stopConversationRef,
      isPrivate
    ],
  );

  const handleRequestApproval = async (conversationId: string) => {
    homeDispatch({ field: 'loading', value: true });
    homeDispatch({ field: 'messageIsStreaming', value: true });

    let { data } = await requestApproval(conversationId)
    let message: Message = { role: "guardrails", content: data.message, msg_info:null, userActionRequired: false };

    let updatedConversation = {
      ...selectedConversation,
      messages: selectedConversation?.messages ? [...selectedConversation?.messages, message] : [message],
    };

    homeDispatch({
      field: 'selectedConversation',
      value: updatedConversation,
    });
    homeDispatch({ field: 'loading', value: false });
    homeDispatch({ field: 'messageIsStreaming', value: false });

  }

  const scrollToBottom = useCallback(() => {
    if (autoScrollEnabled) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      textareaRef.current?.focus();
    }
  }, [autoScrollEnabled]);

  const handleScroll = () => {
    if (chatContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } =
        chatContainerRef.current;
      const bottomTolerance = 30;

      if (scrollTop + clientHeight < scrollHeight - bottomTolerance) {
        setAutoScrollEnabled(false);
        setShowScrollDownButton(true);
      } else {
        setAutoScrollEnabled(true);
        setShowScrollDownButton(false);
      }
    }
  };

  const handleScrollDown = () => {
    chatContainerRef.current?.scrollTo({
      top: chatContainerRef.current.scrollHeight,
      behavior: 'smooth',
    });
  };

  // const handleSettings = () => {
  //   setShowSettings(!showSettings);
  // };

  // const onClearAll = () => {
  //   if (
  //     confirm(('Are you sure you want to clear all messages?')) &&
  //     selectedConversation
  //   ) {
  //     handleUpdateConversation(selectedConversation, {
  //       key: 'messages',
  //       value: [],
  //     });
  //   }
  // };

  const handleModelSelect = (model:Plugin) => {
      setPlugin(model)
  }

  const scrollDown = () => {
    if (autoScrollEnabled) {
      messagesEndRef.current?.scrollIntoView(true);
    }
  };
  const throttledScrollDown = throttle(scrollDown, 250);

  // useEffect(() => {
  //   console.log('currentMessage', currentMessage);
  //   if (currentMessage) {
  //     handleSend(currentMessage);
  //     homeDispatch({ field: 'currentMessage', value: undefined });
  //   }
  // }, [currentMessage]);

  useEffect(() => {
    throttledScrollDown();
    selectedConversation &&
      setCurrentMessage(
        selectedConversation.messages[selectedConversation.messages.length - 2],
      );
  }, [selectedConversation, throttledScrollDown]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        setAutoScrollEnabled(entry.isIntersecting);
        if (entry.isIntersecting) {
          textareaRef.current?.focus();
        }
      },
      {
        root: null,
        threshold: 0.5,
      },
    );
    const messagesEndElement = messagesEndRef.current;
    if (messagesEndElement) {
      observer.observe(messagesEndElement);
    }
    return () => {
      if (messagesEndElement) {
        observer.unobserve(messagesEndElement);
      }
    };
  }, [messagesEndRef]);
  
    const tiles:  JSX.Element[] = [
        <IconBolt size={80} />,
        <IconBook size={80} />,
    ];
  

  return (
    <div className="relative flex-1 overflow-hidden bg-white dark:bg-[#343541]">
      <>
        <div
          className="max-h-full overflow-x-hidden"
          ref={chatContainerRef}
          onScroll={handleScroll}
        >
          {selectedConversation?.messages.length === 0 ? (
            <>
              <div className="mx-auto flex flex-col space-y-5 md:space-y-10 px-3 pt-5 md:pt-12 sm:max-w-[600px]">
                <div className="text-center text-3xl font-semibold text-gray-800 dark:text-gray-100">
                  {models.length === 0 ? (
                    <div className="mx-auto flex h-full w-[300px] flex-col justify-center space-y-6 sm:w-[600px]">
                      <div className="text-center text-4xl font-bold text-black dark:text-white">
                        Welcome to {applicationName}
                      </div>
                      <div className="text-center text-2xl font-bold text-black dark:text-gray-400">
                        Protect your Confidential Information.
                      </div>
                    </div>
                  ) : (
                    'Chatbot UI'
                  )}
                </div>
                <div className='flex gap-10'>
                  {PluginList.map((plug, index) => (
                    <div className={`flex flex-col w-full gap-5 justify-center text-black  rounded-lg border border-neutral-200 p-4 dark:text-gray-400 dark:border-neutral-600 hover:bg-[#595959] dark:hover:bg-[#202123] cursor-pointer ${ plugin === PluginList[index] && 'bg-[#595959] dark:bg-[#202123]'}`}
                      onClick={(e)=>{handleModelSelect(PluginList[index])}}
                    >
                      <div className='flex justify-center'>
                        {tiles[index]}
                      </div>
                      <div className='text-center '>
                        {plug.name}
                      </div>
                    </div>
                    ))}
                </div>
                <div className='w-full justify-center rounded-lg border border-neutral-200 p-4 dark:border-neutral-600'>
                    <PublicPrivateSwitch size={40}/>
                </div>

                {models.length > 0 && (
                  <div className="flex h-full flex-col space-y-4 rounded-lg border border-neutral-200 p-4 dark:border-neutral-600">
                    <ModelSelect />

                    <SystemPrompt
                      conversation={selectedConversation}
                      prompts={prompts}
                      onChangePrompt={(prompt) =>
                        handleUpdateConversation(selectedConversation, {
                          key: 'prompt',
                          value: prompt,
                        })
                      }
                    />

                    <TemperatureSlider
                      label={('Temperature')}
                      onChangeTemperature={(temperature) =>
                        handleUpdateConversation(selectedConversation, {
                          key: 'temperature',
                          value: temperature,
                        })
                      }
                    />
                  </div>
                )}
              </div>
            </>
          ) : (
            <>
              <div className="sticky top-0 z-10 flex justify-center border border-b-neutral-300 bg-neutral-100 py-2 text-sm text-neutral-500 dark:border-none dark:bg-[#444654] dark:text-neutral-200">
                {selectedConversation?.title}

                {/* <button
                    className="ml-2 cursor-pointer hover:opacity-50"
                    onClick={handleSettings}
                  >
                    <IconSettings size={18} />
                  </button>
                  <button
                    className="ml-2 cursor-pointer hover:opacity-50"
                    onClick={onClearAll}
                  >
                    <IconClearAll size={18} />
                  </button> */}
              </div>
              {showSettings && (
                <div className="flex flex-col space-y-10 md:mx-auto md:max-w-xl md:gap-6 md:py-3 md:pt-6 lg:max-w-2xl lg:px-0 xl:max-w-3xl">
                  <div className="flex h-full flex-col space-y-4 border-b border-neutral-200 p-4 dark:border-neutral-600 md:rounded-lg md:border">
                    <ModelSelect />
                  </div>
                </div>
              )}

              {selectedConversation?.messages.map((message, index) => (
                <MemoizedChatMessage
                  key={index}
                  message={message}
                  messageIndex={index}
                  onEdit={(editedMessage) => {
                    setCurrentMessage(editedMessage);
                    // discard edited message and the ones that come after then resend
                    handleSend(
                      editedMessage,
                      selectedConversation?.messages.length - index,
                      plugin
                    );
                  }}
                  onOverRide={(selectedMessage) => {
                    setCurrentMessage(selectedMessage);
                    // discard edited message and the ones that come after then resend
                    handleSend(
                      selectedMessage,
                      selectedConversation?.messages.length - index,
                      plugin,
                      true,
                    );
                  }}
                  onRequestApproval={(conversationId) => {
                    handleRequestApproval(conversationId);
                  }}
                />
              ))}

              {loading && <ChatLoader />}

              <div
                className="h-[162px] bg-white dark:bg-[#343541]"
                ref={messagesEndRef}
              />
            </>
          )}
        </div>

        <ChatInput
          stopConversationRef={stopConversationRef}
          plugin={plugin}
          setPlugin={setPlugin}
          textareaRef={textareaRef}
          onSend={(message, plugin) => {
            setCurrentMessage(message);
            handleSend(message, 0, plugin);
          }}
          onScrollDownClick={handleScrollDown}
          onRegenerate={() => {
            if (currentMessage) {
              handleSend(currentMessage, 2, plugin);
            }
          }}
          showScrollDownButton={showScrollDownButton}
        />
      </>

    </div>
  );
});
Chat.displayName = 'Chat';
