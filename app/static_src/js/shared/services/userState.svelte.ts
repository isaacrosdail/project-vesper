import { UserMeRead } from '../../apiTypes';
import { api } from './api';

export const userState = $state<{ me: UserMeRead | null }>({ me: null });

export async function refreshMe() {
    userState.me = (await api.me.get()).data;
}

export async function patchUser(data: Record<string, string>) {
    await api.user.patch(data);
    await refreshMe();
}
export async function patchProfile(data: Record<string, string>) {
    await api.profile.patch(data);
    await refreshMe();
}
export async function patchGoals(data: Record<string, string>) {
    await api.goals.patch(data);
    await refreshMe();
}
