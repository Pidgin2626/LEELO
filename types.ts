export interface ScheduleRow {
  name: string;
  monday: string;
  tuesday: string;
  wednesday: string;
  thursday: string;
  friday: string;
  saturday: string;
  sunday: string;
  [key: string]: string; // Index signature for dynamic day access
}

export interface TimeEntry {
  name: string;
  date: string;
  in: string;
  out: string;
  hours: number;
  role: string;
}

export interface DayData {
  schedStr: string;
  schedHours: number;
  actualIn: string | null;
  actualOut: string | null;
  actualHours: number;
  delta: number;
  status: 'green' | 'red' | 'orange' | 'noshow' | 'pickup' | 'none';
  role: string;
}

export interface MergedEmployeeData {
  name: string;
  primaryRole: string;
  totalSchedHours: number;
  totalActualHours: number;
  totalDelta: number;
  missedShifts: number;
  days: Record<string, DayData>;
}

export interface RoleTheme {
  bg: string;
  light: string;
  text: string;
}