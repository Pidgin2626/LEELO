import { ScheduleRow, TimeEntry } from "./types";

export const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

// NOTE: This map couples the static "Day Name" to a specific date in the CSVs provided.
// In a dynamic production app, this would likely be handled by selecting a "Week Start Date".
export const DATES_MAP: Record<string, string> = {
  'Monday': 'Dec 01, 2025',
  'Tuesday': 'Dec 02, 2025',
  'Wednesday': 'Dec 03, 2025',
  'Thursday': 'Dec 04, 2025',
  'Friday': 'Dec 05, 2025',
  'Saturday': 'Dec 06, 2025',
  'Sunday': 'Dec 07, 2025',
};

export const DEFAULT_SCHEDULE: ScheduleRow[] = [
  { 
    name: "Jose Baten", 
    monday: "", 
    tuesday: "", 
    wednesday: "", 
    thursday: "", 
    friday: "6pm - 9pm (Cook)", 
    saturday: "2pm - 9pm (Cook)", 
    sunday: "1pm - 8pm (Cook)" 
  },
  { 
    name: "Gustavo Alcala", 
    monday: "", 
    tuesday: "", 
    wednesday: "11am - 6pm (Cook)", 
    thursday: "11am - 4pm (Cook)", 
    friday: "11am - 7pm (Cook)", 
    saturday: "11am - 7pm (Cook)", 
    sunday: "11am - 7pm (Cook)" 
  },
];

export const DEFAULT_TIME_ENTRIES: TimeEntry[] = [
  { 
    name: "Alcala, Gustavo", 
    date: "Dec 01, 2025", 
    in: "03:59 PM", 
    out: "08:13 PM", 
    hours: 4.22, 
    role: "Cook" 
  },
];