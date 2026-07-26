import { UserMeRead } from "../../apiTypes";
import { api } from "./api";

export const userState = $state<{ me: UserMeRead | null }>({ me: null });

export async function refreshMe() {
    userState.me = (await api.me.get()).data;
}
