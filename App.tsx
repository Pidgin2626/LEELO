import React, { useState, useMemo } from 'react';
import { 
  Search, Filter, Clock, User, ChefHat, 
  Utensils, Zap, Users, ChevronDown, 
  AlertCircle, CheckCircle, XCircle, FileText, Upload, 
  Trash2, AlertTriangle, Download, Sun,
  Briefcase, FileDown, ArrowUpDown
} from 'lucide-react';
import { ScheduleRow, TimeEntry, MergedEmployeeData, RoleTheme, DayData } from './types';
import { DAYS, DATES_MAP, DEFAULT_SCHEDULE, DEFAULT_TIME_ENTRIES } from './constants';

// Declare jsPDF on window for TypeScript since we are loading via CDN
declare const window: any;

// --- HELPER FUNCTIONS ---

const normalizeName = (rawName: string): string => {
  if (!rawName) return "Unknown";
  const cleanName = rawName.replace(/^"|"$/g, '').trim();
  
  if (cleanName.includes(',')) {
    const [last, first] = cleanName.split(',').map(s => s.trim());
    // Specific business logic overrides
    if (first === "Byron" && last === "Colop") return "Bryan Colop";
    if (last === "Medina" && first === "Amaireny") return "Amaireny Medina"; 
    return `${first} ${last}`;
  }
  return cleanName;
};

const parseScheduleHours = (timeStr: string | undefined): number => {
  if (!timeStr || timeStr === "OFF") return 0;
  try {
    const range = timeStr.split('(')[0].trim();
    if (!range.includes('-')) return 0;

    const [start, end] = range.split('-').map(t => t.trim());
    
    const parseTime = (t: string): number => {
      if (!t) return 0;
      const match = t.match(/(\d+)(?::(\d+))?\s*(am|pm)/i);
      if (!match) return 0;
      let h = parseInt(match[1]);
      const m = parseInt(match[2] || '0');
      const ampm = match[3].toLowerCase();
      
      if (ampm === 'pm' && h !== 12) h += 12;
      if (ampm === 'am' && h === 12) h = 0;
      return h + (m / 60);
    };

    const startH = parseTime(start);
    let endH = parseTime(end);
    
    // Handle overnight shifts (e.g., 9pm - 2am)
    if (endH < startH) endH += 24; 
    
    return Math.max(0, endH - startH);
  } catch (e) {
    return 0; 
  }
};

const getRoleTheme = (role: string): RoleTheme => {
  const normalized = role?.toLowerCase() || '';
  if (normalized.includes('cook')) return { bg: 'bg-orange-400', light: 'bg-orange-100', text: 'text-orange-900' };
  if (normalized.includes('server')) return { bg: 'bg-cyan-500', light: 'bg-cyan-100', text: 'text-cyan-900' };
  if (normalized.includes('runner')) return { bg: 'bg-teal-500', light: 'bg-teal-100', text: 'text-teal-900' };
  if (normalized.includes('host')) return { bg: 'bg-rose-400', light: 'bg-rose-100', text: 'text-rose-900' };
  if (normalized.includes('busser')) return { bg: 'bg-yellow-400', light: 'bg-yellow-100', text: 'text-yellow-900' };
  return { bg: 'bg-slate-400', light: 'bg-slate-100', text: 'text-slate-800' };
};

const getRoleIcon = (role: string) => {
  const normalized = role?.toLowerCase() || '';
  if (normalized.includes('cook')) return <ChefHat className="w-4 h-4" />;
  if (normalized.includes('server')) return <Utensils className="w-4 h-4" />;
  if (normalized.includes('runner')) return <Zap className="w-4 h-4" />;
  if (normalized.includes('host')) return <User className="w-4 h-4" />;
  if (normalized.includes('busser')) return <Users className="w-4 h-4" />;
  if (normalized.includes('manager')) return <Briefcase className="w-4 h-4" />;
  return <Clock className="w-4 h-4" />;
};

// --- CSV PARSERS ---

const parseCSVLine = (line: string): string[] => {
  const result: string[] = [];
  let current = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === ',' && !inQuotes) {
      result.push(current.trim().replace(/^"|"$/g, ''));
      current = '';
    } else {
      current += char;
    }
  }
  result.push(current.trim().replace(/^"|"$/g, ''));
  return result;
};

const parseTimeEntriesCSV = (text: string): TimeEntry[] => {
  const lines = text.split('\n').filter(line => line.trim() !== '');
  if (lines.length < 2) return [];
  const data: TimeEntry[] = [];
  
  // Start from 1 to skip header
  for (let i = 1; i < lines.length; i++) {
    const cols = parseCSVLine(lines[i]);
    // Basic validation: needs at least name, date, hours
    if (cols.length < 5) continue; 
    
    // Column indices assumption based on user provided data shape
    const entry: TimeEntry = {
      name: cols[0], 
      role: cols[3],
      date: cols[4],
      in: cols[5],
      out: cols[6],
      hours: parseFloat(cols[8] || '0')
    };
    if (entry.name && entry.date) data.push(entry);
  }
  return data;
};

const parseScheduleCSV = (text: string): ScheduleRow[] => {
  const lines = text.split('\n').filter(line => line.trim() !== '');
  if (lines.length < 2) return [];
  const data: ScheduleRow[] = [];
  
  // Start from 1 to skip header
  for (let i = 1; i < lines.length; i++) {
    const cols = parseCSVLine(lines[i]);
    if (cols.length < 8) continue;
    const entry: ScheduleRow = {
      name: cols[0],
      monday: cols[1],
      tuesday: cols[2],
      wednesday: cols[3],
      thursday: cols[4],
      friday: cols[5],
      saturday: cols[6],
      sunday: cols[7]
    };
    if (entry.name) data.push(entry);
  }
  return data;
};

export default function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState('All');
  const [sortBy, setSortBy] = useState<'role' | 'name'>('role');
  const [expandedEmployee, setExpandedEmployee] = useState<string | null>(null);
  
  // Data State
  const [scheduleData, setScheduleData] = useState<ScheduleRow[]>(DEFAULT_SCHEDULE);
  const [timeEntries, setTimeEntries] = useState<TimeEntry[]>(DEFAULT_TIME_ENTRIES);
  
  // UI State
  const [importMode, setImportMode] = useState<'schedule' | 'entries' | null>(null); 
  const [csvText, setCsvText] = useState('');

  // --- HANDLERS ---
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>, type: 'schedule' | 'entries') => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      try {
        if (type === 'schedule') {
          const parsed = parseScheduleCSV(text);
          if (parsed.length) {
            setScheduleData(parsed);
            alert(`Loaded ${parsed.length} schedule rows.`);
          } else throw new Error("No valid rows found");
        } else {
          const parsed = parseTimeEntriesCSV(text);
          if (parsed.length) {
            setTimeEntries(parsed);
            alert(`Loaded ${parsed.length} time entries.`);
          } else throw new Error("No valid rows found");
        }
        setImportMode(null);
      } catch (err) {
        alert("Failed to parse file. Please check format.");
      }
    };
    reader.readAsText(file);
    e.target.value = ''; // Reset input
  };

  const handlePasteImport = () => {
    try {
      if (importMode === 'schedule') {
        const parsed = parseScheduleCSV(csvText);
        if (parsed.length > 0) {
          setScheduleData(parsed);
          setImportMode(null);
          setCsvText('');
        } else {
          alert("Could not parse schedule data.");
        }
      } else {
        const parsed = parseTimeEntriesCSV(csvText);
        if (parsed.length > 0) {
          setTimeEntries(parsed);
          setImportMode(null);
          setCsvText('');
        } else {
          alert("Could not parse time entries.");
        }
      }
    } catch (e: any) {
      alert("Error: " + e.message);
    }
  };

  const clearData = () => {
    if (window.confirm("Clear all loaded data?")) {
      setScheduleData([]);
      setTimeEntries([]);
    }
  };

  // --- DATA MERGING LOGIC ---
  const mergedData: MergedEmployeeData[] = useMemo(() => {
    const schedNames = scheduleData.map(p => p.name);
    const entryNames = timeEntries.map(e => normalizeName(e.name));
    const allNames = Array.from(new Set([...schedNames, ...entryNames])); // Removed .sort() here, done in filteredData

    return allNames.map(name => {
      const schedRecord = scheduleData.find(p => p.name === name);
      
      const dayData: Record<string, DayData> = {};
      let totalSchedHours = 0;
      let totalActualHours = 0;
      let missedShifts = 0;

      DAYS.forEach(day => {
        const dateStr = DATES_MAP[day];
        
        // Use index signature access safely
        const schedStr = schedRecord ? schedRecord[day.toLowerCase()] : "";
        const schedHours = parseScheduleHours(schedStr);
        totalSchedHours += schedHours;

        const dayEntries = timeEntries.filter(e => 
          normalizeName(e.name) === name && e.date === dateStr
        );
        
        const actualHours = dayEntries.reduce((sum, e) => sum + e.hours, 0);
        totalActualHours += actualHours;

        const actualIn = dayEntries.length > 0 ? dayEntries[0].in : null;
        const actualOut = dayEntries.length > 0 ? dayEntries[dayEntries.length-1].out : null;

        let status: DayData['status'] = 'none';
        const delta = actualHours - schedHours;

        if (schedHours > 0 && actualHours > 0) {
          // Rule: If > .5 after schedule (Overtime) -> RED
          if (delta > 0.5) {
            status = 'red'; 
          } 
          // Rule: If < 30 (mins) less than schedule (Undertime) -> ORANGE
          else if (delta < -0.5) {
            status = 'orange';
          } 
          // Rule: Anything between -> GREEN
          else {
            status = 'green';
          }
        } else if (schedHours > 0 && actualHours === 0) {
          status = 'noshow'; 
          missedShifts++;
        } else if (schedHours === 0 && actualHours > 0) {
          status = 'pickup';
        }

        let role = "Staff";
        if (dayEntries.length > 0) role = dayEntries[0].role;
        else if (schedStr) {
          const match = schedStr.match(/\((.*?)\)/);
          if (match) role = match[1];
        }

        dayData[day] = {
          schedStr,
          schedHours,
          actualIn,
          actualOut,
          actualHours,
          delta,
          status,
          role
        };
      });

      const primaryRole = Object.values(dayData).find(d => d.role !== "Staff")?.role || "Staff";

      return {
        name,
        primaryRole,
        totalSchedHours,
        totalActualHours,
        totalDelta: totalActualHours - totalSchedHours,
        missedShifts,
        days: dayData
      };
    });
  }, [scheduleData, timeEntries]);

  // --- FILTERING & SORTING ---
  const filteredData = useMemo(() => {
    // 1. Filter
    const filtered = mergedData.filter(person => {
      // Hide people with absolutely no activity or schedule
      if (person.totalSchedHours === 0 && person.totalActualHours === 0) {
        return false;
      }

      const matchesSearch = person.name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesRole = selectedRole === 'All' || person.primaryRole === selectedRole;
      return matchesSearch && matchesRole;
    });

    // 2. Sort
    return filtered.sort((a, b) => {
      if (sortBy === 'role') {
        const roleComparison = a.primaryRole.localeCompare(b.primaryRole);
        if (roleComparison !== 0) return roleComparison;
      }
      // Secondary sort (or primary if sortBy is 'name')
      return a.name.localeCompare(b.name);
    });
  }, [mergedData, searchTerm, selectedRole, sortBy]);

  // --- DOWNLOAD CSV ---
  const handleDownloadCSV = () => {
    const headers = ["Employee", "Role", "Scheduled Hours", "Actual Hours", "Variance", "Missed Shifts"];
    const rows = filteredData.map(p => [
      `"${p.name}"`,
      p.primaryRole,
      p.totalSchedHours.toFixed(2),
      p.totalActualHours.toFixed(2),
      (p.totalDelta > 0 ? "+" : "") + p.totalDelta.toFixed(2),
      p.missedShifts
    ]);

    const csvContent = [
      headers.join(","),
      ...rows.map(r => r.join(","))
    ].join("\n");

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `LEELO_Report_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // --- GENERATE PDF ---
  const generatePDF = () => {
    if (!window.jspdf) {
      alert("PDF library not loaded. Please check your internet connection.");
      return;
    }

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF('l', 'mm', 'a4'); // Landscape, millimeters, A4

    const tableColumn = ["Employee", "Role", ...DAYS.map(d => d.substring(0,3)), "Var"];
    const tableRows: any[] = [];

    // Data Mapping for PDF
    filteredData.forEach(person => {
      const rowData = [
        person.name,
        person.primaryRole,
      ];

      // Days data
      DAYS.forEach(day => {
        const d = person.days[day];
        let cellText = "";
        
        // Use custom property to style in didParseCell
        if (d.status === 'green') cellText = "OK";
        else if (d.status === 'red') cellText = `+${d.delta.toFixed(1)}h`;
        else if (d.status === 'orange') cellText = `${d.delta.toFixed(1)}h`;
        else if (d.status === 'noshow') cellText = "Missed";
        else if (d.status === 'pickup') cellText = "Extra";
        else cellText = "-";

        rowData.push(cellText);
      });

      // Total Variance
      const totalVarText = (person.totalDelta > 0 ? "+" : "") + person.totalDelta.toFixed(1) + "h";
      rowData.push(totalVarText);

      tableRows.push(rowData);
    });

    // AutoTable Generation
    doc.autoTable({
      head: [tableColumn],
      body: tableRows,
      startY: 25,
      theme: 'grid',
      styles: { fontSize: 8, halign: 'center', valign: 'middle' },
      headStyles: { fillColor: [8, 145, 178] }, // Cyan-600
      columnStyles: {
        0: { halign: 'left', fontStyle: 'bold', cellWidth: 35 }, // Name
        1: { halign: 'left', cellWidth: 25 }, // Role
      },
      didParseCell: function(data: any) {
        if (data.section === 'body' && data.column.index >= 2 && data.column.index <= 8) {
          const text = data.cell.raw;
          if (text === 'Missed') {
            data.cell.styles.fillColor = [254, 202, 202]; // Red-200
            data.cell.styles.textColor = [185, 28, 28]; // Red-700
            data.cell.styles.fontStyle = 'bold';
          } else if (text && text.includes('+') && !text.includes('h')) {
            // Logic for +Delta
            data.cell.styles.fillColor = [254, 202, 202]; // Red-200
            data.cell.styles.textColor = [153, 27, 27]; // Red-800
          } else if (text === 'OK') {
             data.cell.styles.fillColor = [209, 250, 229]; // Emerald-100
             data.cell.styles.textColor = [6, 95, 70]; // Emerald-800
          } else if (text === 'Extra') {
             data.cell.styles.fillColor = [207, 250, 254]; // Cyan-100
             data.cell.styles.textColor = [21, 94, 117]; // Cyan-800
          } else if (text && text.includes('h') && text.startsWith('-')) {
             data.cell.styles.fillColor = [255, 237, 213]; // Orange-100
             data.cell.styles.textColor = [154, 52, 18]; // Orange-800
          } else if (text && text.includes('h') && text.startsWith('+')) {
             data.cell.styles.fillColor = [254, 226, 226]; // Red-100
             data.cell.styles.textColor = [153, 27, 27]; // Red-800
             data.cell.styles.fontStyle = 'bold';
          }
        }
        // Variance Column Styling
        if (data.section === 'body' && data.column.index === 9) {
           const val = parseFloat(data.cell.raw);
           if (val > 0.01) {
             data.cell.styles.textColor = [220, 38, 38]; // Red (Over budget)
             data.cell.styles.fontStyle = 'bold';
           } else {
             data.cell.styles.textColor = [5, 150, 105]; // Green (Under budget or On time)
             data.cell.styles.fontStyle = 'bold';
           }
        }
      }
    });

    // Add Header Info
    const dateStr = new Date().toLocaleDateString();
    doc.setFontSize(18);
    doc.setTextColor(8, 145, 178);
    doc.text("LEELO Schedule Variance Report", 14, 15);
    
    doc.setFontSize(10);
    doc.setTextColor(100);
    doc.text(`Generated: ${dateStr} • Staff Count: ${filteredData.length} • Sorted By: ${sortBy === 'role' ? 'Role' : 'Name'}`, 14, 20);

    // Save
    doc.save(`LEELO_Report_${new Date().toISOString().split('T')[0]}.pdf`);
  };

  // --- STATS ---
  const stats = useMemo(() => {
    const totalMissed = filteredData.reduce((acc, curr) => acc + curr.missedShifts, 0);
    return { totalMissed };
  }, [filteredData]);

  const roles = useMemo(() => {
    const r = new Set(['All']);
    mergedData.forEach(p => r.add(p.primaryRole));
    return Array.from(r).sort();
  }, [mergedData]);

  const getStatusIndicator = (dayInfo: DayData) => {
    switch (dayInfo.status) {
      case 'green': 
        return <div className="w-full h-full bg-emerald-100 rounded flex items-center justify-center border border-emerald-200"><CheckCircle className="w-4 h-4 text-emerald-600" /></div>;
      case 'red': 
        return (
          <div className="w-full h-full rounded flex flex-col items-center justify-center border bg-rose-100 border-rose-200 text-rose-700 text-[10px] font-bold">
            <span>+{dayInfo.delta.toFixed(1)}h</span>
          </div>
        );
      case 'orange': 
        return (
          <div className="w-full h-full rounded flex flex-col items-center justify-center border bg-orange-100 border-orange-200 text-orange-700 text-[10px] font-bold">
            <span>{dayInfo.delta.toFixed(1)}h</span>
          </div>
        );
      case 'noshow':
        return (
          <div className="w-full h-full bg-rose-100 rounded flex items-center justify-center border border-rose-200" title="Missed Shift / No Show">
            <XCircle className="w-4 h-4 text-rose-600" />
          </div>
        );
      case 'pickup':
        return <div className="w-full h-full bg-cyan-100 rounded flex items-center justify-center border border-cyan-200" title="Unscheduled Work"><AlertCircle className="w-4 h-4 text-cyan-600" /></div>;
      default:
        return <div className="w-2 h-2 rounded-full bg-cyan-50/50"></div>;
    }
  };

  return (
    <div className="min-h-screen bg-cyan-50 p-4 md:p-8 font-sans">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* IMPORT MODAL */}
        {importMode && (
          <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full p-6 space-y-4">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                  <Upload className="w-5 h-5 text-cyan-600" />
                  Import {importMode === 'schedule' ? 'Schedule' : 'Time Entries'}
                </h2>
                <button onClick={() => { setImportMode(null); setCsvText(''); }} className="text-slate-400 hover:text-slate-600">
                  <XCircle className="w-6 h-6" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div className="p-4 bg-cyan-50 rounded-lg border border-cyan-200">
                  <p className="text-sm font-medium text-cyan-900 mb-2">Option A: Upload File (.csv)</p>
                  <input 
                    type="file" 
                    accept=".csv"
                    onChange={(e) => handleFileUpload(e, importMode)}
                    className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-cyan-100 file:text-cyan-700 hover:file:bg-cyan-200"
                  />
                </div>
                
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-slate-200"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-white text-slate-500">Or paste text</span>
                  </div>
                </div>

                <div>
                  <p className="text-sm font-medium text-slate-700 mb-2">Option B: Paste CSV Content</p>
                  <textarea
                    className="w-full h-48 border border-slate-200 rounded-lg p-3 font-mono text-xs bg-slate-50 focus:ring-2 focus:ring-cyan-500 focus:outline-none"
                    placeholder="Paste your CSV data here..."
                    value={csvText}
                    onChange={(e) => setCsvText(e.target.value)}
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button 
                  onClick={() => { setImportMode(null); setCsvText(''); }}
                  className="px-4 py-2 text-sm text-slate-600 font-medium hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button 
                  onClick={handlePasteImport}
                  className="px-4 py-2 text-sm text-white bg-cyan-600 font-bold rounded-lg hover:bg-cyan-700 shadow-sm"
                >
                  Process Text
                </button>
              </div>
            </div>
          </div>
        )}

        {/* TOP BAR */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 bg-white p-6 rounded-2xl shadow-sm border border-cyan-200">
          <div>
            <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-teal-500 to-blue-600 flex items-center gap-3">
              <Sun className="w-8 h-8 text-rose-500" />
              LEELO
            </h1>
            <p className="text-slate-500 text-sm mt-1 font-medium">
              Schedule Variance Tracker • {filteredData.length} Staff
            </p>
            {stats.totalMissed > 0 && (
                <div className="flex items-center gap-1 font-bold text-rose-600 bg-rose-50 px-2 py-0.5 rounded-full text-xs mt-2 w-fit border border-rose-200">
                  <AlertTriangle className="w-3 h-3" />
                  {stats.totalMissed} Missed Shifts
                </div>
            )}
          </div>

          <div className="flex flex-wrap gap-3">
            {/* MANAGEMENT REPORTING ACTIONS */}
            <div className="flex gap-2 mr-2 border-r border-slate-200 pr-4">
              <button 
                type="button"
                onClick={generatePDF}
                className="flex items-center justify-center gap-2 px-4 py-2 bg-slate-800 text-white rounded-lg text-sm font-bold hover:bg-slate-700 transition-colors shadow-sm active:scale-95 transform"
              >
                <FileDown className="w-4 h-4" />
                Export PDF
              </button>
              <button 
                onClick={handleDownloadCSV}
                className="flex items-center justify-center gap-2 px-4 py-2 bg-slate-800 text-white rounded-lg text-sm font-bold hover:bg-slate-700 transition-colors shadow-sm active:scale-95 transform"
              >
                <Download className="w-4 h-4" />
                Download CSV
              </button>
            </div>

            <button 
              onClick={() => setImportMode('schedule')}
              className="flex items-center justify-center gap-2 px-4 py-2 bg-white text-cyan-700 rounded-lg text-sm font-bold hover:bg-cyan-50 transition-colors border border-cyan-200 shadow-sm"
            >
              <FileText className="w-4 h-4" />
              Schedule
            </button>
            <button 
              onClick={() => setImportMode('entries')}
              className="flex items-center justify-center gap-2 px-4 py-2 bg-white text-cyan-700 rounded-lg text-sm font-bold hover:bg-cyan-50 transition-colors border border-cyan-200 shadow-sm"
            >
              <Clock className="w-4 h-4" />
              Entries
            </button>
            <button 
              onClick={clearData}
              className="flex items-center justify-center gap-2 px-3 py-2 bg-rose-50 text-rose-400 rounded-lg hover:text-rose-600 hover:bg-rose-100 transition-colors border border-rose-100"
              title="Clear Data"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* CONTROLS */}
        <div className="flex flex-col sm:flex-row justify-between gap-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-cyan-400" />
            <input
              type="text"
              placeholder="Filter by employee name..."
              className="pl-9 pr-4 py-2 bg-white border border-cyan-200 rounded-lg text-sm w-full focus:outline-none focus:ring-2 focus:ring-cyan-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          <div className="flex items-center gap-3 w-full sm:w-auto">
            {/* SORT CONTROL */}
            <div className="relative w-full sm:w-40">
              <ArrowUpDown className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-cyan-400" />
              <select
                className="pl-9 pr-8 py-2 bg-white border border-cyan-200 rounded-lg text-sm w-full focus:outline-none focus:ring-2 focus:ring-cyan-500 appearance-none cursor-pointer"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'role' | 'name')}
              >
                <option value="role">Sort by Role</option>
                <option value="name">Sort by Name</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-cyan-400 pointer-events-none" />
            </div>

            {/* ROLE FILTER */}
            <div className="relative w-full sm:w-48">
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-cyan-400" />
              <select
                className="pl-9 pr-8 py-2 bg-white border border-cyan-200 rounded-lg text-sm w-full focus:outline-none focus:ring-2 focus:ring-cyan-500 appearance-none cursor-pointer"
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
              >
                {roles.map(role => (
                  <option key={role} value={role}>{role}</option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-cyan-400 pointer-events-none" />
            </div>
          </div>
        </div>

        {/* LEGEND */}
        <div className="flex flex-wrap gap-3 text-xs justify-end px-2">
          <div className="flex items-center gap-1.5 bg-white px-2 py-1 rounded border border-cyan-100 shadow-sm">
            <CheckCircle className="w-3 h-3 text-emerald-600" /> <span>On Target (+/- 30m)</span>
          </div>
          <div className="flex items-center gap-1.5 bg-white px-2 py-1 rounded border border-cyan-100 shadow-sm">
            <div className="w-3 h-3 bg-rose-100 border border-rose-200 rounded flex items-center justify-center text-[8px] font-bold text-rose-700">+</div> <span>Overtime (&gt; 30m)</span>
          </div>
          <div className="flex items-center gap-1.5 bg-white px-2 py-1 rounded border border-cyan-100 shadow-sm">
             <div className="w-3 h-3 bg-orange-100 border border-orange-200 rounded flex items-center justify-center text-[8px] font-bold text-orange-700">-</div> <span>Undertime (&lt; 30m)</span>
          </div>
          <div className="flex items-center gap-1.5 bg-white px-2 py-1 rounded border border-cyan-100 shadow-sm">
            <XCircle className="w-3 h-3 text-rose-600" /> <span>Missed Shift</span>
          </div>
        </div>

        {/* MAIN GRID */}
        <div className="bg-white rounded-2xl shadow-sm border border-cyan-200 overflow-hidden">
          <div className="grid grid-cols-[1.5fr,repeat(7,1fr),0.8fr] gap-px bg-cyan-50 border-b border-cyan-200">
            <div className="p-4 font-semibold text-cyan-900 text-sm">Employee</div>
            {DAYS.map((day) => (
              <div key={day} className="p-4 font-semibold text-cyan-900 text-sm text-center hidden md:block">
                {day.substring(0, 3)}
              </div>
            ))}
            <div className="p-4 font-semibold text-cyan-900 text-sm text-right">Variance</div>
          </div>

          <div className="divide-y divide-cyan-100">
            {filteredData.length === 0 ? (
               <div className="p-8 text-center text-slate-500 italic">
                 No active staff found matching your filters.
               </div>
            ) : filteredData.map((person) => {
              const isExpanded = expandedEmployee === person.name;
              const roleTheme = getRoleTheme(person.primaryRole);
              // Strict color logic: Positive = Red, Zero/Negative = Green
              const varianceColor = person.totalDelta > 0.01 ? 'text-rose-600' : 'text-emerald-600';

              return (
                <div key={person.name} className="group transition-colors hover:bg-cyan-50/50">
                  <div 
                    className="grid grid-cols-[1.5fr,repeat(7,1fr),0.8fr] gap-px cursor-pointer"
                    onClick={() => setExpandedEmployee(isExpanded ? null : person.name)}
                  >
                    <div className="p-4 flex items-center gap-3">
                      <div className={`p-2 rounded-full ${roleTheme.light} ${roleTheme.text}`}>
                        {getRoleIcon(person.primaryRole)}
                      </div>
                      <div className="min-w-0">
                        <div className="font-medium text-slate-900 truncate">{person.name}</div>
                        <div className="text-xs text-slate-500 truncate">{person.primaryRole}</div>
                        {person.missedShifts > 0 && (
                          <div className="text-xs text-rose-600 font-bold flex items-center gap-1">
                            <AlertTriangle className="w-3 h-3" />
                            {person.missedShifts} missed
                          </div>
                        )}
                      </div>
                    </div>

                    {DAYS.map((day) => (
                      <div key={day} className="hidden md:flex items-center justify-center p-2">
                        <div className="w-full h-8 max-w-[50px]">
                          {getStatusIndicator(person.days[day])}
                        </div>
                      </div>
                    ))}

                    <div className="p-4 flex flex-col justify-center items-end">
                      <div className={`font-bold text-lg ${varianceColor}`}>
                        {person.totalDelta > 0 ? '+' : ''}{person.totalDelta.toFixed(1)}h
                      </div>
                      <div className="text-xs text-slate-400 mt-1 flex items-center justify-end gap-1.5 opacity-80">
                        <span>Sched: {person.totalSchedHours.toFixed(1)}h</span>
                        <span className="text-slate-300">•</span>
                        <span>Act: {person.totalActualHours.toFixed(1)}h</span>
                      </div>
                    </div>
                  </div>

                  {isExpanded && (
                    <div className="bg-cyan-50 border-t border-cyan-100 p-4 md:p-6 grid grid-cols-1 gap-3 animate-in slide-in-from-top-2 duration-200">
                      <h3 className="text-xs font-bold uppercase text-slate-400 mb-2">Weekly Breakdown</h3>
                      {DAYS.map((day) => {
                        const d = person.days[day];
                        if (d.status === 'none' && !d.schedStr) return null;

                        return (
                          <div key={day} className="bg-white p-3 rounded-lg border border-cyan-200 shadow-sm grid grid-cols-[100px,1fr,1fr,1fr] items-center gap-4">
                            <div className="font-medium text-slate-700">{day}</div>
                            
                            <div className="text-sm">
                              <span className="block text-xs text-slate-400 uppercase">Scheduled</span>
                              {d.schedStr ? (
                                <span className="font-medium text-slate-800">{d.schedStr.split('(')[0]}</span>
                              ) : (
                                <span className="text-slate-400 italic">OFF</span>
                              )}
                            </div>

                            <div className="text-sm">
                              <span className="block text-xs text-slate-400 uppercase">Actual Worked</span>
                              {d.actualIn ? (
                                <span className="font-bold text-slate-900">{d.actualIn} - {d.actualOut}</span>
                              ) : (
                                <span className="text-slate-400">—</span>
                              )}
                            </div>

                            <div className="text-right">
                              {d.status === 'green' && <span className="inline-flex items-center px-2 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold">On Target</span>}
                              {d.status === 'red' && <span className="inline-flex items-center px-2 py-1 rounded-full bg-rose-100 text-rose-800 text-xs font-bold">+{d.delta.toFixed(1)} hrs</span>}
                              {d.status === 'orange' && <span className="inline-flex items-center px-2 py-1 rounded-full bg-orange-100 text-orange-800 text-xs font-bold">{d.delta.toFixed(1)} hrs</span>}
                              {d.status === 'noshow' && <span className="inline-flex items-center px-2 py-1 rounded-full bg-rose-200 text-rose-700 text-xs font-bold">Missed Shift</span>}
                              {d.status === 'pickup' && <span className="inline-flex items-center px-2 py-1 rounded-full bg-cyan-100 text-cyan-800 text-xs font-bold">Extra Shift</span>}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}