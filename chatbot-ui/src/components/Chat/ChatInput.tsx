import {
  IconArrowDown,
  IconBolt,
  IconBrandGoogle,
  IconPlayerStop,
  IconRepeat,
  IconSend,
  IconBook
} from "@tabler/icons-react";

import {
  KeyboardEvent,
  MutableRefObject,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import toast from "react-hot-toast";
import Chip from '@mui/material/Chip';

import { Message } from "@/types/chat";
import { Tile,TilesList } from "@/types/tiles";
import { Prompt } from "@/types/prompt";

import HomeContext from "@/pages/home/home.context";

import { PluginSelect } from "./PluginSelect";
import { PromptList } from "./PromptList";
import { VariableModal } from "./VariableModal";
import { debounce } from "lodash";
import { AnalysisObject, AnalysisResponseType } from "@/types/AnalysisObject";
import { analyzeMessage } from "@/services";
import { AxiosResponse } from "axios";

interface Props {
  onSend: (message: Message, tile: Tile) => void;
  onRegenerate: () => void;
  onScrollDownClick: () => void;
  stopConversationRef: MutableRefObject<boolean>;
  textareaRef: MutableRefObject<HTMLTextAreaElement | null>;
  showScrollDownButton: boolean;
  tile:Tile;
  setTile:Function;
}
const applicationName: string = import.meta.env.VITE_APPLICATION_NAME;

export const ChatInput = ({
  onSend,
  onRegenerate,
  onScrollDownClick,
  stopConversationRef,
  textareaRef,
  showScrollDownButton,
  tile,
  setTile

}: Props) => {
  const {
    state: { selectedConversation, messageIsStreaming, prompts },

    dispatch: homeDispatch,
  } = useContext(HomeContext);

  const [content, setContent] = useState<string>("");
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const [showPromptList, setShowPromptList] = useState(false);
  const [activePromptIndex, setActivePromptIndex] = useState(0);
  const [promptInputValue, setPromptInputValue] = useState("");
  const [variables, setVariables] = useState<string[]>([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [showPluginSelect, setShowPluginSelect] = useState(false);
  
  const [analysisResponse, setAnalysisResponse] = useState<AnalysisObject[]>(
    []
  );

  const promptListRef = useRef<HTMLUListElement | null>(null);

  const filteredPrompts = prompts.filter((prompt) =>
    prompt.name.toLowerCase().includes(promptInputValue.toLowerCase())
  );

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    const maxLength = 2000;

    if (maxLength && value.length > maxLength) {
      alert(
        `Message limit is ${maxLength} characters. You have entered ${value.length} characters.`
      );
      return;
    }

    setContent(value);
    updatePromptListVisibility(value);
  };

  useEffect(() => {
    //fetch message from state
    debounceTimer(content);
    return debounceTimer.cancel;
    //fetch message from state
  }, [content]);

  const debounceTimer = debounce((content) => {
    if (!content.length) {
      setAnalysisResponse([]);
      return;
    }
    analyzeMessage(content)
      .then((res: AxiosResponse<AnalysisResponseType>) => {
        if (res?.data) {
          for (var d of res.data) {
            toast.error(`${d.entity_type} detected : ${d.flagged_text}`, {
              position: 'bottom-right',
              style: {
                color: 'red',
              },
              duration: 7000,
            });
          }
        }
      })
      .catch((err:any) => {
        toast.error(err.message,{
          position:"bottom-right",
          duration:3000
        })
        console.log(err.message, "API ERROR");
      })
      .finally(() => { });
  }, 1000);
  const handleSend = () => {
    if (messageIsStreaming) {
      return;
    }

    if (!content) {
      alert("Please enter a message");
      return;
    }

    onSend({ role: "user", content: content , msg_info: null, userActionRequired: false }, tile);
    setContent("");

    if (window.innerWidth < 640 && textareaRef && textareaRef.current) {
      textareaRef.current.blur();
    }
  };

  const handleStopConversation = () => {
    stopConversationRef.current = true;
    setTimeout(() => {
      stopConversationRef.current = false;
    }, 1000);
  };

  const isMobile = () => {
    const userAgent =
      typeof window.navigator === "undefined" ? "" : navigator.userAgent;
    const mobileRegex =
      /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini|Mobile|mobile|CriOS/i;
    return mobileRegex.test(userAgent);
  };

  const handleInitModal = () => {
    const selectedPrompt = filteredPrompts[activePromptIndex];
    if (selectedPrompt) {
      setContent((prevContent) => {
        const newContent = prevContent?.replace(
          /\/\w*$/,
          selectedPrompt.content
        );
        return newContent;
      });
      handlePromptSelect(selectedPrompt);
    }
    setShowPromptList(false);
  };

  const toggleShowPluginSelect = () => {
    if(selectedConversation?.messages?.length && showPluginSelect == false)
    {
      return
    }
    setShowPluginSelect(!showPluginSelect)
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (showPromptList) {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setActivePromptIndex((prevIndex) =>
          prevIndex < prompts.length - 1 ? prevIndex + 1 : prevIndex
        );
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setActivePromptIndex((prevIndex) =>
          prevIndex > 0 ? prevIndex - 1 : prevIndex
        );
      } else if (e.key === "Tab") {
        e.preventDefault();
        setActivePromptIndex((prevIndex) =>
          prevIndex < prompts.length - 1 ? prevIndex + 1 : 0
        );
      } else if (e.key === "Enter") {
        e.preventDefault();
        handleInitModal();
      } else if (e.key === "Escape") {
        e.preventDefault();
        setShowPromptList(false);
      } else {
        setActivePromptIndex(0);
      }
    } else if (e.key === "Enter" && !isTyping && !isMobile() && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    } else if (e.key === "/" && e.metaKey) {
      e.preventDefault();
      setShowPluginSelect(!showPluginSelect);
    }
  };

  const parseVariables = (content: string) => {
    const regex = /{{(.*?)}}/g;
    const foundVariables = [];
    let match;

    while ((match = regex.exec(content)) !== null) {
      foundVariables.push(match[1]);
    }

    return foundVariables;
  };

  const updatePromptListVisibility = useCallback((text: string) => {
    const match = text.match(/\/\w*$/);

    if (match) {
      setShowPromptList(true);
      setPromptInputValue(match[0].slice(1));
    } else {
      setShowPromptList(false);
      setPromptInputValue("");
    }
  }, []);

  const handlePromptSelect = (prompt: Prompt) => {
    const parsedVariables = parseVariables(prompt.content);
    setVariables(parsedVariables);

    if (parsedVariables.length > 0) {
      setIsModalVisible(true);
    } else {
      setContent((prevContent) => {
        const updatedContent = prevContent?.replace(/\/\w*$/, prompt.content);
        return updatedContent;
      });
      updatePromptListVisibility(prompt.content);
    }
  };

  const handleSubmit = (updatedVariables: string[]) => {
    const newContent = content?.replace(/{{(.*?)}}/g, (match, variable) => {
      const index = variables.indexOf(variable);
      return updatedVariables[index];
    });

    setContent(newContent);

    if (textareaRef && textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  useEffect(() => {
    if(!selectedConversation?.messages.length || selectedConversation.model == "gpt-3.5-turbo")
    {
      setTile(TilesList[0])
    }
    else if(selectedConversation?.model == "private-docs"){
      setTile(TilesList[1])
    }
    else if(selectedConversation?.model == "private-docs-private-llm"){
      setTile(TilesList[2])
    }

  }, [selectedConversation]);


  useEffect(() => {
    if (promptListRef.current) {
      promptListRef.current.scrollTop = activePromptIndex * 30;
    }
  }, [activePromptIndex]);

  useEffect(() => {
    if (textareaRef && textareaRef.current) {
      textareaRef.current.style.height = "inherit";
      textareaRef.current.style.height = `${textareaRef.current?.scrollHeight}px`;
      textareaRef.current.style.overflow = `${textareaRef?.current?.scrollHeight > 400 ? "auto" : "hidden"
        }`;
    }
  }, [content]);

  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (
        promptListRef.current &&
        !promptListRef.current.contains(e.target as Node)
      ) {
        setShowPromptList(false);
      }
    };

    window.addEventListener("click", handleOutsideClick);

    return () => {
      window.removeEventListener("click", handleOutsideClick);
    };
  }, []);

  return (
    <div className="absolute bottom-0 left-0 w-full border-transparent bg-gradient-to-b from-transparent via-white to-white pt-6 dark:border-white/20 dark:via-[#343541] dark:to-[#343541] md:pt-2">
      <div className="stretch mx-2 mt-4 flex flex-row gap-3 last:mb-2 md:mx-4 md:mt-[52px] md:last:mb-6 lg:mx-auto lg:max-w-3xl">
        {/* {messageIsStreaming && (
          <button
            className="absolute top-0 left-0 right-0 mx-auto mb-3 flex w-fit items-center gap-3 rounded border border-neutral-200 bg-white py-2 px-4 text-black hover:opacity-50 dark:border-neutral-600 dark:bg-[#343541] dark:text-white md:mb-0 md:mt-2"
            onClick={handleStopConversation}
          >
            <IconPlayerStop size={16} /> {"Stop Generating"}
          </button>
        )} */}
{/* 
        {!messageIsStreaming && !selectedConversation?.archived &&
          selectedConversation &&
          selectedConversation.messages.length > 0 && (
            <button
              className="absolute top-0 left-0 right-0 mx-auto mb-3 flex w-fit items-center gap-3 rounded border border-neutral-200 bg-white py-2 px-4 text-black hover:opacity-50 dark:border-neutral-600 dark:bg-[#343541] dark:text-white md:mb-0 md:mt-2"
              onClick={onRegenerate}
            >
              <IconRepeat size={16} /> {"Regenerate response"}
            </button>
          )} */}

        <div className="relative mx-2 flex w-full flex-grow flex-col rounded-md border border-black/10 bg-white shadow-[0_0_10px_rgba(0,0,0,0.10)] dark:border-gray-900/50 dark:bg-[#40414F] dark:text-white dark:shadow-[0_0_15px_rgba(0,0,0,0.10)] sm:mx-4">
          {/* <button
            className="absolute left-2 top-2 rounded-sm p-1 text-neutral-800 opacity-60 hover:bg-neutral-200 hover:text-neutral-900 dark:bg-opacity-50 dark:text-neutral-100 dark:hover:text-neutral-200"
            onClick={() => toggleShowPluginSelect() }
            onKeyDown={(e) => { }}
            style={{opacity: selectedConversation?.messages?.length!=0? "10%" : ""}}
          >
            {plugin.id == PluginList[0].id ? <IconBolt size={20} /> : <IconBook size={20} />}
          </button> */}
          {/* {plugin can only be changed if conversation is empty} */}
          {/* {showPluginSelect && (
            <div className="absolute left-0 bottom-14 rounded bg-white dark:bg-[#343541]">
              <PluginSelect
                plugin={plugin}
                onKeyDown={(e: any) => {
                  if (e.key === "Escape") {
                    e.preventDefault();
                    setShowPluginSelect(false);
                    textareaRef.current?.focus();
                  }
                }}
                onPluginChange={(plugin: Plugin) => {
                  setPlugin(plugin);
                  setShowPluginSelect(false);

                  if (textareaRef && textareaRef.current) {
                    textareaRef.current.focus();
                  }
                }}
              />
            </div>
          )} */}

          <textarea
            ref={textareaRef} disabled={selectedConversation?.archived}
            className="m-0 w-full resize-none border-0 bg-transparent p-0 py-2 pr-8 pl-10 text-black dark:bg-transparent dark:text-white md:py-3 md:pl-10"
            style={{
              resize: "none",
              bottom: `${textareaRef?.current?.scrollHeight}px`,
              maxHeight: "400px",
              overflow: `${textareaRef.current && textareaRef.current.scrollHeight > 400
                  ? "auto"
                  : "hidden"
                }`,
            }}
            placeholder={
              'Type a message or type "/" to select a prompt...' || ""
            }
            value={content}
            rows={1}
            onCompositionStart={() => setIsTyping(true)}
            onCompositionEnd={() => setIsTyping(false)}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
          />

          <button
            className="absolute right-2 top-2 rounded-sm p-1 text-neutral-800 opacity-60 hover:bg-neutral-200 hover:text-neutral-900 dark:bg-opacity-50 dark:text-neutral-100 dark:hover:text-neutral-200"
            onClick={handleSend}
          >
            {messageIsStreaming ? (
              <div className="h-4 w-4 animate-spin rounded-full border-t-2 border-neutral-800 opacity-60 dark:border-neutral-100"></div>
            ) : (
              <IconSend size={18} />
            )}
          </button>

          {showScrollDownButton && (
            <div className="absolute bottom-12 right-0 lg:bottom-0 lg:-right-10">
              <button
                className="flex h-7 w-7 items-center justify-center rounded-full bg-neutral-300 text-gray-800 shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-neutral-200"
                onClick={onScrollDownClick}
              >
                <IconArrowDown size={18} />
              </button>
            </div>
          )}

          {showPromptList && filteredPrompts.length > 0 && (
            <div className="absolute bottom-12 w-full">
              <PromptList
                activePromptIndex={activePromptIndex}
                prompts={filteredPrompts}
                onSelect={handleInitModal}
                onMouseOver={setActivePromptIndex}
                promptListRef={promptListRef}
              />
            </div>
          )}

          {isModalVisible && (
            <VariableModal
              prompt={filteredPrompts[activePromptIndex]}
              variables={variables}
              onSubmit={handleSubmit}
              onClose={() => setIsModalVisible(false)}
            />
          )}
        </div>
      </div>
      <div className="px-3 pt-2 pb-3 text-center text-[12px] text-black/50 dark:text-white/50 md:px-4 md:pt-3 md:pb-6">
        {applicationName}
        <Chip label="Beta" variant="outlined" size="small" style={{ borderColor: '#DA9B14', color: '#DA9B14' ,width:'39px',height:'15px',fontSize:'10px', margin:'2px'}} />
        lets your organisation use public LLM models in a safe and secure way, ensuring your corporate confidential information remains protected.
      </div>
    </div>
  );
};
