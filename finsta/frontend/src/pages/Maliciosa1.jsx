import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Maliciosa1() {
  const navigate = useNavigate();
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-purple-50 text-gray-900">
      {/* Warning banner - only visible in demo */}
      <div className="bg-red-600 text-white text-center py-2 text-xs font-bold tracking-wide">
        SIMULACION FLOWLENS — ESTA PAGINA ES FALSA — DEMO HACKATHON
      </div>

      {/* Nav */}
      <nav className="bg-white/80 backdrop-blur shadow-sm">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">&#9733;</span>
            <span className="text-xl font-bold bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
              Elite Models International
            </span>
          </div>
          <div className="hidden md:flex gap-6 text-sm text-gray-600">
            <span className="cursor-pointer hover:text-pink-600">Inicio</span>
            <span className="cursor-pointer hover:text-pink-600">Modelos</span>
            <span className="cursor-pointer hover:text-pink-600">Destinos</span>
            <span className="cursor-pointer hover:text-pink-600">Contacto</span>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="max-w-5xl mx-auto px-6 py-16 md:py-24 grid md:grid-cols-2 gap-10 items-center">
          <div>
            <div className="inline-block bg-pink-100 text-pink-700 text-xs font-bold px-3 py-1 rounded-full mb-4">
              CASTING ABIERTO 2026
            </div>
            <h1 className="text-4xl md:text-5xl font-extrabold leading-tight">
              Tu carrera como <span className="text-pink-600">modelo internacional</span> comienza aqui
            </h1>
            <p className="mt-4 text-lg text-gray-600 leading-relaxed">
              Viaja a <strong>Paris, Milan y Nueva York</strong> con todos los gastos pagados.
              No necesitas experiencia previa — nosotros te entrenamos.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <div className="flex items-center gap-2 bg-white rounded-full px-4 py-2 shadow-sm text-sm">
                <span>&#9992;</span> Vuelos pagados
              </div>
              <div className="flex items-center gap-2 bg-white rounded-full px-4 py-2 shadow-sm text-sm">
                <span>&#127960;</span> Hotel 5 estrellas
              </div>
              <div className="flex items-center gap-2 bg-white rounded-full px-4 py-2 shadow-sm text-sm">
                <span>&#128176;</span> $2,000 - $10,000 por sesion
              </div>
            </div>
          </div>
          <div className="relative">
            <img
              src="https://picsum.photos/id/1027/600/800"
              alt="Modelo"
              className="w-full rounded-2xl shadow-2xl object-cover"
            />
            <div className="absolute -bottom-4 -left-4 bg-white rounded-xl shadow-lg p-3 text-sm">
              <div className="font-bold text-pink-600">+2,400 modelos</div>
              <div className="text-gray-500 text-xs">colocadas internacionalmente</div>
            </div>
          </div>
        </div>
      </section>

      {/* Application form */}
      <section className="bg-white py-16">
        <div className="max-w-xl mx-auto px-6">
          <h2 className="text-2xl font-bold text-center mb-2">Aplica al casting exclusivo</h2>
          <p className="text-center text-gray-500 text-sm mb-8">
            Completa tus datos y te contactaremos en 24 horas
          </p>

          {submitted ? (
            <div className="bg-green-50 border border-green-200 rounded-2xl p-8 text-center">
              <div className="text-4xl mb-3">&#10003;</div>
              <h3 className="font-bold text-lg text-green-800">Solicitud recibida</h3>
              <p className="text-green-600 text-sm mt-2">
                Nuestro equipo revisara tu perfil. Te contactaremos por WhatsApp o email.
              </p>
              <button
                onClick={() => navigate("/")}
                className="mt-4 text-sm text-pink-600 underline"
              >
                Volver a Finsta
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Nombre completo *</label>
                  <input
                    type="text"
                    required
                    className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-pink-500 focus:border-pink-500 outline-none"
                    placeholder="Tu nombre"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Edad *</label>
                  <input
                    type="number"
                    required
                    min="16"
                    max="30"
                    className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-pink-500 focus:border-pink-500 outline-none"
                    placeholder="18"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Correo electronico *</label>
                <input
                  type="email"
                  required
                  className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-pink-500 focus:border-pink-500 outline-none"
                  placeholder="tu@email.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">WhatsApp *</label>
                <input
                  type="tel"
                  required
                  className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-pink-500 focus:border-pink-500 outline-none"
                  placeholder="+506 8888-8888"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Ciudad y pais *</label>
                <input
                  type="text"
                  required
                  className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-pink-500 focus:border-pink-500 outline-none"
                  placeholder="San Jose, Costa Rica"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Sube 3 fotos recientes (cuerpo completo) *
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center cursor-pointer hover:border-pink-400 transition-colors">
                  <div className="text-2xl mb-1">&#128247;</div>
                  <p className="text-sm text-gray-500">Arrastra tus fotos o haz clic</p>
                  <p className="text-xs text-gray-400 mt-1">JPG, PNG hasta 10MB</p>
                  <input type="file" multiple accept="image/*" className="hidden" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Numero de pasaporte (opcional para viaje)
                </label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-pink-500 focus:border-pink-500 outline-none"
                  placeholder="Tu numero de pasaporte"
                />
              </div>
              <button
                type="submit"
                className="w-full bg-gradient-to-r from-pink-600 to-purple-600 text-white py-3 rounded-xl font-bold text-sm hover:opacity-90 transition-opacity"
              >
                Enviar mi aplicacion
              </button>
              <p className="text-xs text-gray-400 text-center">
                Al enviar aceptas nuestros terminos y condiciones.
              </p>
            </form>
          )}
        </div>
      </section>

      {/* Red flags footer for demo awareness */}
      <div className="bg-red-50 border-t-2 border-red-300 py-6 px-6">
        <div className="max-w-3xl mx-auto">
          <h3 className="font-bold text-red-700 text-sm mb-2">
            INDICADORES DE RIESGO DETECTADOS POR FLOWLENS:
          </h3>
          <ul className="text-xs text-red-600 space-y-1 list-disc list-inside">
            <li>Solicita datos de pasaporte antes de cualquier contrato</li>
            <li>Promete viajes internacionales "todo pagado" sin verificacion</li>
            <li>Pide fotos de cuerpo completo a desconocidos</li>
            <li>Dominio registrado hace solo 12 dias</li>
            <li>No tiene informacion legal, registro mercantil ni direccion verificable</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
