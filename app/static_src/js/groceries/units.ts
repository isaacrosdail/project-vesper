import { ProductCategoryEnum, UnitEnum } from "../apiTypes";


type Dimension = 'mass' | 'volume' | 'count';

const UNIT_DIMENSION = {
    g: 'mass', kg: 'mass', oz: 'mass', lb: 'mass',
    ml: 'volume', l: 'volume', fl_oz: 'volume',
    ea: 'count',
} as const satisfies Record<UnitEnum, Dimension>;

const CATEGORY_DIMENSIONS = {
    beverages: ["volume"],
    condiments_sauces: ["volume"],
    fruits: ["mass"],
    vegetables: ["mass"], 
    legumes: ["mass"],
    grains: ["mass"],
    bakery: ["mass"],
    meats: ["mass"],
    seafood: ["mass"],
    snacks: ["mass"],
    sweets: ["mass"],
    processed_convenience: ["mass", "volume"],
    supplements: ["mass", "volume"],
    dairy_eggs: ["mass", "volume"],
    fats_oils: ["mass", "volume"],
} as const satisfies Record<ProductCategoryEnum, readonly Dimension[]>;

export const ALL_UNITS = Object.keys(UNIT_DIMENSION) as UnitEnum[];
export const CATEGORIES = Object.keys(CATEGORY_DIMENSIONS) as ProductCategoryEnum[];

export function unitsFor(category: ProductCategoryEnum | ''): UnitEnum[] {
    if (!category) return ALL_UNITS;
    const dims = CATEGORY_DIMENSIONS[category];
    return ALL_UNITS.filter(u => dims.includes(UNIT_DIMENSION[u]));
}
