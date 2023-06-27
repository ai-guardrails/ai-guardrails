import {
  IconFileExport,
  IconSettings,
  IconArchive,
  IconArchiveOff,
  IconLogout
} from "@tabler/icons-react";
import { useContext, useState } from "react";

import HomeContext from "@/pages/home/home.context";

import { SettingDialog } from "@/components/Settings/SettingDialog";

import { Import } from "../../Settings/Import";
import { Key } from "../../Settings/Key";
import { SidebarButton } from "../../Sidebar/SidebarButton";
import ChatbarContext from "../Chatbar.context";
import { ClearConversations } from "./ClearConversations";
import { PluginKeys } from "./PluginKeys";
import { AuthContext } from "@/services/AuthService";

export const ChatbarSettings = () => {
  const [isSettingDialogOpen, setIsSettingDialog] = useState<boolean>(false);
  const authContext = useContext(AuthContext)

  const {
    state: {
      apiKey,
      lightMode,
      serverSideApiKeyIsSet,
      serverSidePluginKeysSet,
      conversations,
      isArchiveView,
    },
    dispatch: homeDispatch,
  } = useContext(HomeContext);

  const {
    handleClearConversations,
    handleExportData,
  } = useContext(ChatbarContext);

  const handleIsArchiveView = () => {
    homeDispatch({ field: "isArchiveView", value: !isArchiveView });
  };

  return (
    <div className="flex flex-col items-center space-y-1 border-t border-black/20 pt-1 text-sm">
      {conversations.length > 0 && !isArchiveView ? (
        <ClearConversations onClearConversations={handleClearConversations} />
      ) : null}
      {/* <Import onImport={handleImportConversations} /> */}

      {/* <SidebarButton
        text={('Export data')}
        icon={<IconFileExport size={18} />}
        onClick={() => handleExportData()}
      /> */}

      {isArchiveView ? (
        <SidebarButton
          text={"Active Chats"}
          icon={<IconArchiveOff size={18} />}
          onClick={() => handleIsArchiveView()}
        />
      ) : (
        <SidebarButton
          text={"Archived Chats"}
          icon={<IconArchive size={18} />}
          onClick={() => handleIsArchiveView()}
        />
      )}

      <SidebarButton
        text={"Settings"}
        icon={<IconSettings size={18} />}
        onClick={() => setIsSettingDialog(true)}
      />

    <SidebarButton
        text={"Log Out"}
        icon={<IconLogout size={18} />}
        onClick={() => authContext.logout()}
      />
      <SettingDialog
        open={isSettingDialogOpen}
        onClose={() => {
          setIsSettingDialog(false);
        }}
      />
    </div>
  );
};
