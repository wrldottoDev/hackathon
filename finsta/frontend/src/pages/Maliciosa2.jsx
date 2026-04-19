import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Maliciosa2() {
  const navigate = useNavigate();
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 text-gray-900">
      {/* Warning banner */}
      <div className="bg-red-600 text-white text-center py-2 text-xs font-bold tracking-wide">
        SIMULACION FLOWLENS — ESTA PAGINA ES FALSA — DEMO HACKATHON
      </div>

      {/* Nav */}
      <nav className="bg-white/80 backdrop-blur shadow-sm">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">&#128188;</span>
            <span className="text-xl font-bold text-blue-700">
              TrabajoGlobal<span className="text-green-500">YA</span>
            </span>
          </div>
          <div className="hidden md:flex gap-6 text-sm text-gray-600">
            <span className="cursor-pointer hover:text-blue-600">Empleos</span>
            <span className="cursor-pointer hover:text-blue-600">Testimonios</span>
            <span className="cursor-pointer hover:text-blue-600">FAQ</span>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-5xl mx-auto px-6 py-16 md:py-24 grid md:grid-cols-2 gap-10 items-center">
        <div>
          <div className="inline-block bg-green-100 text-green-700 text-xs font-bold px-3 py-1 rounded-full mb-4">
            +500 VACANTES DISPONIBLES
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold leading-tight">
            Gana <span className="text-green-600">$3,000 — $5,000 USD</span> al mes
          </h1>
          <p className="mt-4 text-lg text-gray-600 leading-relaxed">
            Empleos en <strong>Estados Unidos, Canada y Europa</strong>.
            <br />
            <strong>Sin experiencia</strong> necesaria. Nosotros gestionamos tu visa y pasaje.
          </p>
          <div className="mt-6 grid grid-cols-2 gap-3">
            {[
              ["&#9989;", "Sin experiencia"],
              ["&#128176;", "Paga inmediata en USD"],
              ["&#9992;", "Pasaje aereo incluido"],
              ["&#127968;", "Alojamiento gratis"],
              ["&#128196;", "Visa gestionada"],
              ["&#128241;", "Solo necesitas WhatsApp"],
            ].map(([icon, text], i) => (
              <div
                key={i}
                className="flex items-center gap-2 bg-white rounded-xl px-3 py-2.5 shadow-sm text-sm"
              >
                <span dangerouslySetInnerHTML={{ __html: icon }} />
                <span>{text}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="space-y-4">
          <img
            src="https://picsum.photos/id/1076/600/400"
            alt="Trabajo"
            className="w-full rounded-2xl shadow-xl object-cover"
          />
          <div className="bg-white rounded-xl shadow-md p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-lg">
                &#128100;
              </div>
              <div>
                <div className="font-bold text-sm">Carlos M.</div>
                <div className="text-xs text-gray-500">Bogota → Toronto</div>
              </div>
            </div>
            <p className="text-sm text-gray-600 italic">
              "Aplique sin experiencia y en 2 semanas ya estaba en Canada ganando en dolares.
              La mejor decision de mi vida."
            </p>
            <div className="flex gap-1 mt-2 text-yellow-400 text-xs">
              {"★★★★★"}
            </div>
          </div>
        </div>
      </section>

      {/* Form */}
      <section className="bg-white py-16">
        <div className="max-w-xl mx-auto px-6">
          <h2 className="text-2xl font-bold text-center mb-2">Registrate para una vacante</h2>
          <p className="text-center text-gray-500 text-sm mb-6">
            Cupos limitados — Solo quedan <span className="text-red-500 font-bold">12 vacantes</span> este mes
          </p>

          {submitted ? (
            <div className="bg-green-50 border border-green-200 rounded-2xl p-8 text-center">
              <div className="text-4xl mb-3">&#10003;</div>
              <h3 className="font-bold text-lg text-green-800">Registro exitoso</h3>
              <p className="text-green-600 text-sm mt-2">
                Un asesor te contactara por WhatsApp en las proximas horas
                para coordinar tu proceso de visa y viaje.
              </p>
              <button
                onClick={() => navigate("/")}
                className="mt-4 text-sm text-blue-600 underline"
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
                    className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    placeholder="Tu nombre"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Edad *</label>
                  <input
                    type="number"
                    required
                    min="18"
                    max="55"
                    className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    placeholder="25"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">WhatsApp *</label>
                <input
                  type="tel"
                  required
                  className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  placeholder="+506 8888-8888"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Pais de residencia *</label>
                <select
                  required
                  className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                >
                  <option value="">Selecciona</option>
                  <option>Costa Rica</option>
                  <option>Colombia</option>
                  <option>Honduras</option>
                  <option>Guatemala</option>
                  <option>Nicaragua</option>
                  <option>El Salvador</option>
                  <option>Venezuela</option>
                  <option>Ecuador</option>
                  <option>Peru</option>
                  <option>Otro</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tienes pasaporte vigente? *
                </label>
                <div className="flex gap-4 mt-1">
                  <label className="flex items-center gap-2 text-sm">
                    <input type="radio" name="passport" value="si" required className="accent-blue-600" />
                    Si
                  </label>
                  <label className="flex items-center gap-2 text-sm">
                    <input type="radio" name="passport" value="no" className="accent-blue-600" />
                    No (te ayudamos a tramitarlo)
                  </label>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Deposito de gestion de visa: $150 USD
                </label>
                <p className="text-xs text-gray-400 mb-2">
                  Reembolsable una vez iniciado el empleo
                </p>
                <select className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm">
                  <option>Transferencia bancaria</option>
                  <option>Western Union</option>
                  <option>SINPE Movil</option>
                </select>
              </div>
              <button
                type="submit"
                className="w-full bg-gradient-to-r from-blue-600 to-green-600 text-white py-3 rounded-xl font-bold text-sm hover:opacity-90 transition-opacity"
              >
                Asegurar mi vacante
              </button>
            </form>
          )}
        </div>
      </section>

      {/* Red flags footer */}
      <div className="bg-red-50 border-t-2 border-red-300 py-6 px-6">
        <div className="max-w-3xl mx-auto">
          <h3 className="font-bold text-red-700 text-sm mb-2">
            INDICADORES DE RIESGO DETECTADOS POR FLOWLENS:
          </h3>
          <ul className="text-xs text-red-600 space-y-1 list-disc list-inside">
            <li>Solicita deposito de dinero antes de iniciar el trabajo</li>
            <li>Promete empleo "sin experiencia" con salarios irrealistas</li>
            <li>"Visa gestionada" sin ser un agente migratorio autorizado</li>
            <li>Usa urgencia artificial ("solo quedan 12 vacantes")</li>
            <li>Dominio registrado hace solo 5 dias</li>
            <li>Testimonios no verificables — fotos de stock</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
