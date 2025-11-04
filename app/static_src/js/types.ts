
// '.. = HTMLDialogElement & { ..' tells TS "it's a dialog element BUT it also has these specific dataset properties"
export type FormDialog = HTMLDialogElement & {
    dataset: {
        endpoint?: string;
        mode?: string;
        itemId?: string;
        subtype?: string;
    }
}

export type WeatherResult = {
    temp: number | string;
    emoji: string;
    sunsetFormatted: string;
    sunrise: number | null;
    sunset: number | null;
}