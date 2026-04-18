export const DEMO_BANKS = [
  {
    bank_name: "Banco A",
    bank_code: "BKA",
    api_url: import.meta.env.VITE_BANK_A_API_URL || "http://127.0.0.1:8001",
    status: "active",
  },
  {
    bank_name: "Banco B",
    bank_code: "BKB",
    api_url: import.meta.env.VITE_BANK_B_API_URL || "http://127.0.0.1:8002",
    status: "active",
  },
];
