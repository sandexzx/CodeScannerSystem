import { useState, useEffect } from 'react';
import { useCodeContext } from '../contexts/CodeContext';
import { Cog6ToothIcon, CheckCircleIcon, TrashIcon } from '@heroicons/react/24/outline';

export const Settings = () => {
  const { boxCapacity, onUpdateBoxCapacity, session } = useCodeContext();
  const [capacity, setCapacity] = useState(boxCapacity.toString());
  const [showSaved, setShowSaved] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [clearError, setClearError] = useState<string | null>(null);

  // Email settings state
  const [smtpHost, setSmtpHost] = useState("");
  const [smtpPort, setSmtpPort] = useState("587");
  const [smtpUsername, setSmtpUsername] = useState("");
  const [smtpPassword, setSmtpPassword] = useState("");
  const [smtpUseTls, setSmtpUseTls] = useState(true);
  const [mailFrom, setMailFrom] = useState("");
  const [mailTo, setMailTo] = useState("");
  const [savingEmail, setSavingEmail] = useState(false);
  const [sendingExcel, setSendingExcel] = useState(false);
  const [emailMessage, setEmailMessage] = useState<string | null>(null);

  // Update local state when boxCapacity changes
  useEffect(() => {
    setCapacity(boxCapacity.toString());
  }, [boxCapacity]);

  // Handle save
  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    const newCapacity = parseInt(capacity, 10);
    if (!isNaN(newCapacity) && newCapacity > 0) {
      onUpdateBoxCapacity(newCapacity);
      setShowSaved(true);
      setTimeout(() => setShowSaved(false), 2000);
    }
  };

  // Handle clear export
  const handleClearExport = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/settings/clear-export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to clear export folders');
      }
      
      setShowConfirmDialog(false);
      setClearError(null);
    } catch (error: any) {
      setClearError(error.message);
    }
  };

  // Load settings (including email settings) on mount
  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch('http://localhost:5001/api/settings');
        if (!res.ok) return;
        const cfg = await res.json();
        if (cfg) {
          setSmtpHost(cfg.smtp_host || "");
          setSmtpPort(String(cfg.smtp_port || "587"));
          setSmtpUsername(cfg.smtp_username || "");
          setSmtpPassword(cfg.smtp_password || "");
          setSmtpUseTls(cfg.smtp_use_tls === undefined ? true : Boolean(cfg.smtp_use_tls));
          setMailFrom(cfg.mail_from || "");
          setMailTo(cfg.mail_to || "");
        }
      } catch (e) {
        // ignore load errors for settings
      }
    };
    load();
  }, []);

  const saveEmailSettings = async () => {
    setSavingEmail(true);
    setEmailMessage(null);
    try {
      const payload = {
        smtp_host: smtpHost,
        smtp_port: Number(smtpPort || 587),
        smtp_username: smtpUsername,
        smtp_password: smtpPassword,
        smtp_use_tls: smtpUseTls,
        mail_from: mailFrom,
        mail_to: mailTo
      };
      const res = await fetch('http://localhost:5001/api/settings/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const json = await res.json();
      if (!res.ok) {
        throw new Error(json.error || json.message || 'Failed to save email settings');
      }
      setEmailMessage('Настройки почты сохранены');
    } catch (err: any) {
      setEmailMessage(`Ошибка: ${err.message}`);
    } finally {
      setSavingEmail(false);
      setTimeout(() => setEmailMessage(null), 4000);
    }
  };

  const sendExcel = async () => {
    setSendingExcel(true);
    setEmailMessage(null);
    try {
      const res = await fetch('http://localhost:5001/api/send-excel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const json = await res.json();
      if (!res.ok) {
        throw new Error(json.message || json.error || 'Failed to send excel');
      }
      setEmailMessage('Excel отправлен успешно');
    } catch (err: any) {
      setEmailMessage(`Ошибка при отправке: ${err.message}`);
    } finally {
      setSendingExcel(false);
      setTimeout(() => setEmailMessage(null), 6000);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-medium text-gray-900 dark:text-white">Настройки</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Настройка параметров приложения
        </p>
      </div>

      <div className="flex-1 p-6 bg-gray-50 dark:bg-gray-900 overflow-y-auto">
        <div className="max-w-3xl mx-auto space-y-6">
          <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                Вместимость коробки
              </h3>
              <div className="mt-2 max-w-xl text-sm text-gray-500 dark:text-gray-400">
                <p>
                  Установите максимальное количество предметов, которые могут поместиться в коробку.
                </p>
              </div>
              
              <form onSubmit={handleSave} className="mt-6">
                <div className="w-full sm:max-w-xs">
                  <label htmlFor="capacity" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Вместимость коробки
                  </label>
                  <div className="relative rounded-md shadow-sm">
                    <input
                      type="number"
                      name="capacity"
                      id="capacity"
                      min="1"
                      value={capacity}
                      onChange={(e) => setCapacity(e.target.value)}
                      className="block w-full px-4 py-3 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 sm:text-sm transition-colors duration-200 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                      placeholder="например: 10"
                    />
                  </div>
                </div>
                <div className="mt-4">
                  <button
                    type="submit"
                    className="inline-flex items-center justify-center px-4 py-2 border border-transparent shadow-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:focus:ring-offset-gray-800 sm:text-sm transition-colors duration-200"
                  >
                    {showSaved ? (
                      <>
                        <CheckCircleIcon className="-ml-1 mr-2 h-5 w-5 text-green-400" />
                        Saved
                      </>
                    ) : (
                      'Сохранить'
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                Управление экспортом
              </h3>
              <div className="mt-2 max-w-xl text-sm text-gray-500 dark:text-gray-400">
                <p>
                  Очистить все экспортированные файлы из папок экспорта. Это действие нельзя отменить.
                </p>
                {session && (
                  <p className="mt-2 text-yellow-600 dark:text-yellow-400">
                    ⚠️ Невозможно очистить папки экспорта во время активной сессии сканирования. Пожалуйста, завершите текущую сессию.
                  </p>
                )}
                {clearError && (
                  <p className="mt-2 text-red-600 dark:text-red-400">
                    Ошибка: {clearError}
                  </p>
                )}
              </div>
              <div className="mt-5">
                <button
                  type="button"
                  onClick={() => setShowConfirmDialog(true)}
                  disabled={!!session}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 dark:focus:ring-offset-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <TrashIcon className="-ml-1 mr-2 h-5 w-5" />
                  Очистить папки экспорта
                </button>
              </div>
            </div>
          </div>

          {/* Email settings and send button */}
          <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg mt-6">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                Настройки почты и отправка Excel
              </h3>
              <div className="mt-2 max-w-3xl text-sm text-gray-500 dark:text-gray-400">
                <p>Заполните настройки SMTP и нажмите «Сохранить настройки почты». После этого можно отправить последний сформированный Excel.</p>
              </div>

              <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">SMTP Host</label>
                  <input value={smtpHost} onChange={(e) => setSmtpHost(e.target.value)} className="mt-1 block w-full px-3 py-2 rounded-md border bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">SMTP Port</label>
                  <input value={smtpPort} onChange={(e) => setSmtpPort(e.target.value)} className="mt-1 block w-full px-3 py-2 rounded-md border bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Username</label>
                  <input value={smtpUsername} onChange={(e) => setSmtpUsername(e.target.value)} className="mt-1 block w-full px-3 py-2 rounded-md border bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Password</label>
                  <input type="password" value={smtpPassword} onChange={(e) => setSmtpPassword(e.target.value)} className="mt-1 block w-full px-3 py-2 rounded-md border bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
                </div>
                <div className="sm:col-span-2">
                  <label className="inline-flex items-center">
                    <input type="checkbox" checked={smtpUseTls} onChange={(e) => setSmtpUseTls(e.target.checked)} className="mr-2" />
                    <span className="text-sm text-gray-700 dark:text-gray-300">Use TLS (STARTTLS)</span>
                  </label>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">From</label>
                  <input value={mailFrom} onChange={(e) => setMailFrom(e.target.value)} className="mt-1 block w-full px-3 py-2 rounded-md border bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">To</label>
                  <input value={mailTo} onChange={(e) => setMailTo(e.target.value)} className="mt-1 block w-full px-3 py-2 rounded-md border bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
                </div>
              </div>

              <div className="mt-4 flex space-x-3">
                <button
                  type="button"
                  onClick={saveEmailSettings}
                  disabled={savingEmail}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
                >
                  {savingEmail ? "Сохраняю..." : "Сохранить настройки почты"}
                </button>

                <button
                  type="button"
                  onClick={sendExcel}
                  disabled={sendingExcel || !!session}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50"
                >
                  {sendingExcel ? "Отправка..." : "Отправить последний Excel"}
                </button>
              </div>

              {emailMessage && (
                <p className="mt-3 text-sm text-gray-700 dark:text-gray-300">{emailMessage}</p>
              )}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                О программе
              </h3>
              <div className="mt-2 max-w-xl text-sm text-gray-500 dark:text-gray-400">
                <p>
                  Сканер DataMatrix
                </p>
                <p className="mt-2">
                  Современный интерфейс для сканирования и управления кодами DataMatrix.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Confirmation Dialog */}
      {showConfirmDialog && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-md w-full p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Подтверждение очистки папок экспорта
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
              Это действие навсегда удалит все файлы в папках экспорта. Это нельзя отменить.
              Пожалуйста, убедитесь, что вы сохранили все важные данные перед продолжением.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setShowConfirmDialog(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-md"
              >
                Отмена
              </button>
              <button
                type="button"
                onClick={handleClearExport}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md"
              >
                Очистить
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Settings;
