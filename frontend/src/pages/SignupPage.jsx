import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { UserPlus, Mail, Lock, Key, Loader2, ArrowLeft } from 'lucide-react';

const SignupPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [code, setCode] = useState('');
  const [step, setStep] = useState(1); // 1: Registration, 2: Confirmation
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register, confirmRegistration } = useAuth();
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(email, password);
      setStep(2);
    } catch (err) {
      setError(err.message || 'Failed to sign up');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await confirmRegistration(email, code);
      navigate('/login');
    } catch (err) {
      setError(err.message || 'Failed to confirm');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-emerald-500 rounded-2xl mb-4 shadow-lg shadow-emerald-500/20">
            <UserPlus className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{step === 1 ? 'Create Account' : 'Verify Email'}</h1>
          <p className="text-gray-500 font-medium">{step === 1 ? 'Join LakeChat AI Analytics' : 'Enter verification code'}</p>
        </div>

        {step === 1 ? (
          <form onSubmit={handleRegister} className="space-y-6">
            {error && <div className="p-4 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm font-medium">{error}</div>}
            
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 rounded-xl py-3 pl-11 pr-4 text-gray-900 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium"
                  placeholder="name@company.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 rounded-xl py-3 pl-11 pr-4 text-gray-900 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-bold py-3 rounded-xl transition-all shadow-lg shadow-emerald-500/25 flex items-center justify-center gap-2"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Register'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleConfirm} className="space-y-6">
            {error && <div className="p-4 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm font-medium">{error}</div>}
            
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2">Verification Code</label>
              <div className="relative">
                <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 rounded-xl py-3 pl-11 pr-4 text-gray-900 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-center text-2xl tracking-[0.5em] font-bold"
                  placeholder="000000"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-bold py-3 rounded-xl transition-all shadow-lg shadow-emerald-500/25 flex items-center justify-center gap-2"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Confirm Account'}
            </button>
            <button
              type="button"
              onClick={() => setStep(1)}
              className="w-full text-gray-500 hover:text-gray-700 flex items-center justify-center gap-2 text-sm font-bold"
            >
              <ArrowLeft className="w-4 h-4" /> Change Email
            </button>
          </form>
        )}

        <p className="text-center mt-8 text-gray-500 text-sm font-medium">
          Already have an account? <Link to="/login" className="text-blue-600 hover:text-blue-700 font-bold">Sign In</Link>
        </p>
      </div>
    </div>
  );
};

export default SignupPage;
