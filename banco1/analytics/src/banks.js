export const BANKS = [
  {
    id: "banco1",
    label: "Banco 1",
    apiUrl: import.meta.env.VITE_BANCO1_API_URL || "http://127.0.0.1:8000",
    description: "Instancia demo inicial del simulador bancario.",
  },
  {
    id: "banco2",
    label: "Banco 2",
    apiUrl: import.meta.env.VITE_BANCO2_API_URL || "http://127.0.0.1:8001",
    description: "Segunda instancia bancaria conectada a la consola externa.",
  },
  {
    id: "banco3",
    label: "Banco 3",
    apiUrl: import.meta.env.VITE_BANCO3_API_URL || "http://127.0.0.1:8002",
    description: "Tercera instancia bancaria lista para análisis cruzado.",
  },
  // Agrega aqui futuros conectores como banco4, banco5, etc.
];

export function getBankById(bankId) {
  return BANKS.find((bank) => bank.id === bankId) || BANKS[0];
}
