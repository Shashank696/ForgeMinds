import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Brain, Mail, Lock, User, Building2, Eye, EyeOff, ArrowRight } from 'lucide-react';
import useAuth from '../hooks/useAuth';
import { APP_NAME } from '../utils/constants';

const LoginPage = () => {
  const [activeTab, setActiveTab] = useState('signin');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  const { login, register } = useAuth();

  const [signInForm, setSignInForm] = useState({ email: '', password: '' });
  const [signUpForm, setSignUpForm] = useState({
    full_name: '',
    email: '',
    password: '',
    department: '',
  });

  const handleSignIn = async (e) => {
    e.preventDefault();
    setError('');

    if (!signInForm.email || !signInForm.password) {
      setError('Please fill in all required fields.');
      return;
    }

    setIsSubmitting(true);
    try {
      await login(signInForm.email, signInForm.password);
      navigate('/');
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || 'Login failed. Please check your credentials.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    setError('');

    if (!signUpForm.full_name || !signUpForm.email || !signUpForm.password) {
      setError('Please fill in all required fields.');
      return;
    }

    setIsSubmitting(true);
    try {
      await register(signUpForm);
      navigate('/');
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || 'Registration failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card animate-fade-in-up">
        <div className="login-logo">
          <div className="login-logo-icon">
            <Brain size={32} />
          </div>
          <h1>{APP_NAME}</h1>
          <p className="login-subtitle">Industrial Knowledge Intelligence Platform</p>
        </div>

        <div className="login-tabs">
          <button
            className={`login-tab ${activeTab === 'signin' ? 'active' : ''}`}
            onClick={() => { setActiveTab('signin'); setError(''); }}
          >
            Sign In
          </button>
          <button
            className={`login-tab ${activeTab === 'signup' ? 'active' : ''}`}
            onClick={() => { setActiveTab('signup'); setError(''); }}
          >
            Sign Up
          </button>
        </div>

        {error && (
          <div className="login-error animate-fade-in">
            <span>{error}</span>
          </div>
        )}

        {activeTab === 'signin' ? (
          <form className="login-form" onSubmit={handleSignIn}>
            <div className="form-group">
              <label htmlFor="signin-email">Email</label>
              <div className="input-with-icon">
                <Mail size={18} className="input-icon" />
                <input
                  id="signin-email"
                  type="email"
                  placeholder="you@company.com"
                  value={signInForm.email}
                  onChange={(e) => setSignInForm({ ...signInForm, email: e.target.value })}
                  autoComplete="email"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="signin-password">Password</label>
              <div className="input-with-icon">
                <Lock size={18} className="input-icon" />
                <input
                  id="signin-password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={signInForm.password}
                  onChange={(e) => setSignInForm({ ...signInForm, password: e.target.value })}
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-lg login-submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <span className="btn-loading">Signing in…</span>
              ) : (
                <>
                  Sign In
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>
        ) : (
          <form className="login-form" onSubmit={handleSignUp}>
            <div className="form-group">
              <label htmlFor="signup-name">Full Name *</label>
              <div className="input-with-icon">
                <User size={18} className="input-icon" />
                <input
                  id="signup-name"
                  type="text"
                  placeholder="Jane Doe"
                  value={signUpForm.full_name}
                  onChange={(e) => setSignUpForm({ ...signUpForm, full_name: e.target.value })}
                  autoComplete="name"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="signup-email">Email *</label>
              <div className="input-with-icon">
                <Mail size={18} className="input-icon" />
                <input
                  id="signup-email"
                  type="email"
                  placeholder="you@company.com"
                  value={signUpForm.email}
                  onChange={(e) => setSignUpForm({ ...signUpForm, email: e.target.value })}
                  autoComplete="email"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="signup-password">Password *</label>
              <div className="input-with-icon">
                <Lock size={18} className="input-icon" />
                <input
                  id="signup-password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Create a password"
                  value={signUpForm.password}
                  onChange={(e) => setSignUpForm({ ...signUpForm, password: e.target.value })}
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="signup-department">Department</label>
              <div className="input-with-icon">
                <Building2 size={18} className="input-icon" />
                <input
                  id="signup-department"
                  type="text"
                  placeholder="e.g. Engineering"
                  value={signUpForm.department}
                  onChange={(e) => setSignUpForm({ ...signUpForm, department: e.target.value })}
                />
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-lg login-submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <span className="btn-loading">Creating account…</span>
              ) : (
                <>
                  Create Account
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>
        )}

        <div className="login-footer">
          <Link to="/landing" className="login-back-link">← Back to landing page</Link>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
