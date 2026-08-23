/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type ScheduleTypeEnum = "frequency" | "weekly" | "monthly" | "interval";
export type ProductCategoryEnum =
  | "fruits"
  | "vegetables"
  | "legumes"
  | "grains"
  | "bakery"
  | "dairy_eggs"
  | "meats"
  | "seafood"
  | "fats_oils"
  | "snacks"
  | "sweets"
  | "beverages"
  | "condiments_sauces"
  | "processed_convenience"
  | "supplements";
export type MealEnum = "breakfast" | "morning_snack" | "lunch" | "afternoon_snack" | "supper" | "pm_snack";
export type WeightUnitsEnum = "lbs" | "kg";
export type TargetKind = "at_least" | "at_most" | "within";
export type TargetStatus = "good" | "over" | "under";
export type UnitEnum = "g" | "kg" | "oz" | "lb" | "ml" | "l" | "fl_oz" | "ea";
export type HabitTypeEnum = "binary" | "numeric_value" | "duration";
export type InventoryLedgerEventTypeEnum = "purchase" | "consumption" | "correction" | "waste";
export type PriorityEnum = "low" | "medium" | "high" | "frog";
export type UnitSystemEnum = "metric" | "imperial";
export type HourCycleEnum = "h12" | "h23";
export type SexEnum = "m" | "f";

export interface BinaryHabitCreate {
  name: string;
  pillar_ids?: number[];
  schedule_type: ScheduleTypeEnum;
  weekly_frequency?: number | null;
  scheduled_days?: [number, ...number[]] | null;
  monthly_days?: [number, ...number[]] | null;
  interval_days?: number | null;
  start_date?: string | null;
  end_date?: string | null;
  type: "binary";
}
export interface CategorySpendRead {
  category: ProductCategoryEnum;
  spent: number;
  pct: number;
}
export interface CookRequest {
  meal: MealEnum;
  entry_datetime: string;
}
export interface DailyMetricsCreate {
  entry_date: string;
  weight?: number | null;
  weight_units?: WeightUnitsEnum | null;
  steps?: number | null;
  calories?: number | null;
  wake_datetime?: string | null;
  sleep_datetime?: string | null;
}
export interface DailyMetricsPointRead {
  date: string;
  value: number | null;
}
export interface DailyMetricsRead {
  id: number;
  entry_datetime: string;
  weight: number | null;
  steps: number | null;
  calories: number | null;
  wake_datetime: string | null;
  sleep_datetime: string | null;
  sleep_duration_minutes: number | null;
  created_at: string;
  subtype: "daily_metrics";
}
export interface DashboardIntakeRead {
  targets: MacrosSummaryRead;
  cals_avg_daily: number;
  days_on_target: number | null;
  total_cals_over_period: number;
  num_meals_logged: number;
  days_logged: number;
  status: TargetStatus | null;
  meals_today: {
    [k: string]: number;
  };
}
export interface MacrosSummaryRead {
  calories: MacroLineRead;
  protein: MacroLineRead;
  carbs: MacroLineRead;
  fat: MacroLineRead;
  sodium: MacroLineRead;
  potassium: MacroLineRead;
}
export interface MacroLineRead {
  actual: number;
  target: TargetRead | null;
  pct: number | null;
  target_status: TargetStatus | null;
}
export interface TargetRead {
  low: number | null;
  high: number | null;
  nominal: number | null;
  threshold: number | null;
  kind: TargetKind | null;
}
export interface DashboardMidsectionRead {
  num_meals_logged: number;
  top_five_recipes_cooked: RecipeCookedRead[];
  total_spent: number;
  category_spends: CategorySpendRead[];
  shopping_list_items: ShoppingListItemRead[];
}
export interface RecipeCookedRead {
  id: number;
  name: string;
  count: number;
}
export interface ShoppingListItemRead {
  id: number;
  shopping_list_id: number;
  product_id: number;
  product_name: string;
  category: ProductCategoryEnum;
  quantity_wanted: number;
  is_checked: boolean;
  net_weight: number;
  unit_type: UnitEnum;
  created_at: string;
  subtype: "shopping_list_items";
  last_price: number | null;
}
export interface DashboardPurchaseInsightsRead {
  top_products: [unknown, unknown][];
  num_transactions: number;
  num_products: number;
  total_spent: number;
  num_trips: number;
  last_shopping_trip: LastShoppingTripRead | null;
}
export interface LastShoppingTripRead {
  id: number;
  store_name: string;
  entry_datetime: string;
  total_price: number;
  num_transactions: number;
}
export interface DurationHabitCreate {
  name: string;
  pillar_ids?: number[];
  schedule_type: ScheduleTypeEnum;
  weekly_frequency?: number | null;
  scheduled_days?: [number, ...number[]] | null;
  monthly_days?: [number, ...number[]] | null;
  interval_days?: number | null;
  start_date?: string | null;
  end_date?: string | null;
  type: "duration";
  target?: (AtLeastCreate | AtMostCreate | WithinCreate) | null;
}
export interface AtLeastCreate {
  kind: "at_least";
  value: number;
}
export interface AtMostCreate {
  kind: "at_most";
  value: number;
}
export interface WithinCreate {
  kind: "within";
  value: number;
  tolerance: number;
}
export interface GroceriesDashboardPayload {
  intake: DashboardIntakeRead;
  purchase_insights: DashboardPurchaseInsightsRead;
  midsection: DashboardMidsectionRead;
}
export interface HabitCompletionCreate {
  entry_date: string;
  value: number | null;
}
export interface HabitCompletionProgressRead {
  completed: number;
  total: number;
  percent: number;
}
export interface HabitCompletionRead {
  id: number;
  habit_id: number;
  entry_date: string;
  value: number | null;
  created_at: string;
  subtype: "habit_completions";
}
export interface HabitCreateBase {
  name: string;
  pillar_ids?: number[];
  schedule_type: ScheduleTypeEnum;
  weekly_frequency?: number | null;
  scheduled_days?: [number, ...number[]] | null;
  monthly_days?: [number, ...number[]] | null;
  interval_days?: number | null;
  start_date?: string | null;
  end_date?: string | null;
}
export interface HabitDayRead {
  entry_date: string;
  value: number | null;
  target: TargetRead | null;
  satisfied: boolean;
}
export interface HabitOverviewItemRead {
  id: number;
  name: string;
  created_at: string;
  pillars: PillarRead[];
  subtype: "habits";
  type: HabitTypeEnum;
  units: string | null;
  target: TargetRead | null;
  schedule_type: ScheduleTypeEnum;
  weekly_frequency: number | null;
  scheduled_days: number[] | null;
  monthly_days: number[] | null;
  interval_days: number | null;
  start_date: string;
  end_date: string | null;
  completed_today: boolean;
  streak_count: number;
  data: HabitDayRead[];
  consistency: number | null;
  week_intended: string[] | null;
}
export interface PillarRead {
  id: number;
  name: string;
}
export interface HabitPatch {
  name?: string | null;
  pillar_ids?: number[] | null;
  units?: string | null;
  target?: (AtLeastCreate | AtMostCreate | WithinCreate) | null;
  schedule_type?: ScheduleTypeEnum | null;
  weekly_frequency?: number | null;
  scheduled_days?: [number, ...number[]] | null;
  monthly_days?: [number, ...number[]] | null;
  interval_days?: number | null;
  start_date?: string | null;
  end_date?: string | null;
}
export interface HabitRead {
  id: number;
  name: string;
  created_at: string;
  pillars: PillarRead[];
  subtype: "habits";
  type: HabitTypeEnum;
  units: string | null;
  target: TargetRead | null;
  schedule_type: ScheduleTypeEnum;
  weekly_frequency: number | null;
  scheduled_days: number[] | null;
  monthly_days: number[] | null;
  interval_days: number | null;
  start_date: string;
  end_date: string | null;
}
export interface HabitStatsRead {
  id: number;
  name: string;
  created_at: string;
  pillars: PillarRead[];
  subtype: "habits";
  type: HabitTypeEnum;
  units: string | null;
  target: TargetRead | null;
  schedule_type: ScheduleTypeEnum;
  weekly_frequency: number | null;
  scheduled_days: number[] | null;
  monthly_days: number[] | null;
  interval_days: number | null;
  start_date: string;
  end_date: string | null;
  days_missed: number;
  best_streak: number;
}
export interface InventoryLedgerCreate {
  qty_delta: number;
  event_type: InventoryLedgerEventTypeEnum;
  note?: string | null;
}
export interface LogProductRequest {
  product_id: number;
  grams: string;
  meal: MealEnum;
  entry_datetime: string;
}
export interface MetricsWindowQuery {
  lastNDays: number;
  metric_type?: ("weight" | "steps" | "calories" | "sleep_duration_minutes") | null;
}
export interface NumericHabitCreate {
  name: string;
  pillar_ids?: number[];
  schedule_type: ScheduleTypeEnum;
  weekly_frequency?: number | null;
  scheduled_days?: [number, ...number[]] | null;
  monthly_days?: [number, ...number[]] | null;
  interval_days?: number | null;
  start_date?: string | null;
  end_date?: string | null;
  type: "numeric_value";
  units?: string | null;
  target?: (AtLeastCreate | AtMostCreate | WithinCreate) | null;
}
export interface NutritionLogCreate {
  entry_datetime: string;
  meal: MealEnum;
  calories?: number | null;
  protein?: number | null;
  fat?: number | null;
  carbs?: number | null;
  fat_mono?: number | null;
  fat_poly?: number | null;
  fat_sat?: number | null;
  carbs_fiber?: number | null;
  carbs_sugar?: number | null;
  sodium?: number | null;
  potassium?: number | null;
}
export interface ProductCreate {
  name: string;
  category: ProductCategoryEnum;
  barcode?: string | null;
  net_weight: string;
  unit_type: UnitEnum;
  calories_per_100g?: number | null;
  protein_per_100g?: number | null;
  fat_per_100g?: number | null;
  fat_mono_per_100g?: number | null;
  fat_poly_per_100g?: number | null;
  fat_sat_per_100g?: number | null;
  carbs_per_100g?: number | null;
  carbs_fiber_per_100g?: number | null;
  carbs_sugar_per_100g?: number | null;
  sodium_per_100g?: number | null;
  potassium_per_100g?: number | null;
}
export interface ProductInventoryCreate {
  qty_on_hand: number;
}
export interface ProductPatch {
  name?: string | null;
  category?: ProductCategoryEnum | null;
  barcode?: string | null;
  net_weight?: string | null;
  unit_type?: UnitEnum | null;
  calories_per_100g?: number | null;
  protein_per_100g?: number | null;
  fat_per_100g?: number | null;
  fat_mono_per_100g?: number | null;
  fat_poly_per_100g?: number | null;
  fat_sat_per_100g?: number | null;
  carbs_per_100g?: number | null;
  carbs_fiber_per_100g?: number | null;
  carbs_sugar_per_100g?: number | null;
  sodium_per_100g?: number | null;
  potassium_per_100g?: number | null;
}
export interface ProductRead {
  id: number;
  name: string;
  category: ProductCategoryEnum;
  barcode: string | null;
  net_weight: number;
  unit_type: UnitEnum;
  calories_per_100g: number | null;
  protein_per_100g: number | null;
  fat_per_100g: number | null;
  carbs_per_100g: number | null;
  fat_mono_per_100g: number | null;
  fat_poly_per_100g: number | null;
  fat_sat_per_100g: number | null;
  carbs_fiber_per_100g: number | null;
  carbs_sugar_per_100g: number | null;
  sodium_per_100g: number | null;
  potassium_per_100g: number | null;
  created_at: string;
  subtype: "products";
}
export interface RecipeCreate {
  name: string;
  yields: string;
  yields_units: UnitEnum;
  ingredients?: RecipeIngredientCreate[];
}
export interface RecipeIngredientCreate {
  product_id: number;
  amount_value: string;
  amount_units: UnitEnum;
}
export interface RecipeIngredientRead {
  product_id: number;
  product_name: string;
  amount_value: number;
  amount_units: UnitEnum;
}
export interface RecipePatch {
  name?: string | null;
  yields?: string | null;
  yields_units?: UnitEnum | null;
  ingredients?: RecipeIngredientCreate[] | null;
}
export interface RecipeRead {
  id: number;
  name: string;
  yields: number;
  yields_units: UnitEnum;
  ingredients: RecipeIngredientRead[];
  created_at: string;
  subtype: "recipes";
}
export interface RecipeSlotRead {
  id: number;
  name: string;
  yields: number | null;
  yields_units: UnitEnum | null;
  missing: ShortfallRead[];
}
export interface ShortfallRead {
  product_id: number;
  product_name: string;
  deficit_value: number;
  unit: UnitEnum;
}
export interface ShoppingListCreate {
  name: string;
}
export interface ShoppingListItemCreate {
  product_id: number;
  quantity_wanted: number;
}
export interface ShoppingListItemPatch {
  quantity_wanted?: number | null;
  is_checked?: boolean | null;
}
export interface ShoppingTripCreate {
  store_name: string;
  entry_datetime: string;
  /**
   * @minItems 1
   */
  lines: [ShoppingTripLine, ...ShoppingTripLine[]];
}
export interface ShoppingTripLine {
  product_id: number;
  price_at_scan: string;
  quantity: number;
}
export interface TaskCreate {
  name: string;
  priority: PriorityEnum;
  due_datetime?: string | null;
  subtask_ids?: number[];
  supertask_ids?: number[];
  pillar_ids?: number[];
}
export interface TaskLink {
  subtask_id: number;
  supertask_id: number;
}
export interface TaskPatch {
  name?: string | null;
  priority?: PriorityEnum | null;
  due_datetime?: string | null;
  subtask_ids?: number[] | null;
  supertask_ids?: number[] | null;
  pillar_ids?: number[] | null;
  completed_at?: string | null;
  sort_key?: string | null;
}
export interface TaskProgressRead {
  completed: number;
  total: number;
  percent: number;
}
export interface TaskRead {
  id: number;
  name: string;
  priority: PriorityEnum;
  due_datetime: string | null;
  sort_key: string;
  completed_at: string | null;
  created_at: string;
  is_done: boolean;
  subtasks: number[];
  supertasks: number[];
  pillars: PillarRead[];
  subtype: "tasks";
}
export interface TaskStatRead {
  rate: number;
  count: number;
  total: number;
}
export interface TimeEntryCreate {
  entry_date: string;
  category: string;
  description?: string | null;
  started_at: string;
  ended_at: string;
  pillar_ids?: number[];
}
export interface TimeEntryPatch {
  entry_date?: string | null;
  category?: string | null;
  description?: string | null;
  started_at?: string | null;
  ended_at?: string | null;
  pillar_ids?: number[] | null;
}
export interface TimeEntryRead {
  id: number;
  category: string;
  description: string | null;
  started_at: string;
  ended_at: string;
  duration_minutes: number;
  pillars: PillarRead[];
  created_at: string;
  subtype: "time_entries";
}
export interface TransactionCreate {
  product_id?: number | null;
  product?: ProductCreate | null;
  price_at_scan: string;
  quantity: number;
}
export interface TransactionPatch {
  price_at_scan?: string | null;
  quantity?: number | null;
}
export interface TransactionRead {
  id: number;
  product_id: number;
  product_name: string;
  shopping_trip_id: number | null;
  price_at_scan: number;
  quantity: number;
  price_per_100g: number;
  net_weight: number;
  unit_type: UnitEnum;
  created_at: string;
  subtype: "transactions";
}
export interface UserGoalsPatch {
  weight?: number | null;
  calories?: number | null;
  steps?: number | null;
  sleep_duration_minutes?: number | null;
  protein_pct?: number | null;
  fat_pct?: number | null;
  carbs_pct?: number | null;
  potassium?: number | null;
  sodium?: number | null;
}
export interface UserGoalsRead {
  weight: number | null;
  calories: number | null;
  steps: number | null;
  sleep_duration_minutes: number | null;
  protein_pct: number | null;
  protein: number | null;
  fat_pct: number | null;
  fat: number | null;
  carbs_pct: number | null;
  carbs: number | null;
  potassium: number | null;
  sodium: number | null;
}
export interface UserMeRead {
  is_owner: boolean;
  timezone: string;
  profile: UserProfileRead;
  goals: UserGoalsRead;
}
export interface UserProfileRead {
  city: string | null;
  country: string | null;
  unit_system: UnitSystemEnum;
  hour_cycle: HourCycleEnum;
  sex: SexEnum | null;
  birth_date: string | null;
  height_cm: number | null;
  latitude: number | null;
  longitude: number | null;
}
export interface UserPatch {
  name?: string | null;
  timezone?: string | null;
}
export interface UserProfilePatch {
  city?: string | null;
  state?: string | null;
  country?: string | null;
  unit_system?: UnitSystemEnum | null;
  hour_cycle?: HourCycleEnum | null;
  sex?: SexEnum | null;
  birth_date?: string | null;
  height_cm?: number | null;
}
export interface UserRegister {
  username: string;
  password: string;
  name?: string | null;
  timezone: string;
}
