import { FC, useContext, ChangeEvent } from "react";
import HomeContext from "@/pages/home/home.context";

import PublicPrivateSwitch from "@/components/PublicPrivateSwitch";
import { Tile, TilesList } from "@/types/tiles";

interface Props {}

export const PromptbarSettings: FC<Props> = () => {
  const {
    state: { selectedConversation, selectedTile },
    handleSelectedTile,
  } = useContext(HomeContext);

  const handleChange = (event: ChangeEvent<HTMLSelectElement>) => {
    handleSelectedTile(
      TilesList.find((tile) => tile.task == event.target.value) as Tile
    );
  };

  return (
    <>
      {selectedConversation?.messages.length != 0 ? (
        <div className="border-t border-white/40 pt-6">
          <label
            htmlFor="tilelist"
            className="block mb-2 text-sm font-medium text-white"
          >
            Select Task
          </label>
          <select
            id="tilelist"
            value={selectedTile.task}
            className="bg-[#343541]  text-white border border-gray-600 placeholder-gray-400 text-sm rounded-lg focus:ring-white-500 focus:border-white-500 block w-full p-2.5"
            onChange={handleChange}
          >
            {TilesList.map((tile, index) => (
                <option value={tile.task} key={index} className="py-2">{tile.displayName}
                </option>
           
              ))}
          </select>
          <PublicPrivateSwitch size={25} />
        </div>
      ) : (
        <></>
      )}
    </>
  );
};
