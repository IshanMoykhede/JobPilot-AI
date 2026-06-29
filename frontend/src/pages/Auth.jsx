import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Icon from '../components/common/Icon';

function Auth() {
  const [view, setView] = useState("login"); // "login" | "signup" | "forgot"
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [forgotStep, setForgotStep] = useState("request"); // "request" | "reset"

  const { login, register, user, loading, hasProfile } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user && !loading && hasProfile !== null) {
      if (hasProfile) {
        navigate('/dashboard', { replace: true });
      } else {
        navigate('/profile', { replace: true });
      }
    }
  }, [user, loading, hasProfile, navigate]);

  const switchView = (newView) => {
    setView(newView);
    setError("");
    setSuccess("");
    setName("");
    setEmail("");
    setPassword("");
    setOtp("");
    setForgotStep("request");
    setShowPassword(false);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      const { hasProfile } = await login({ email, password });
      if (hasProfile) navigate("/dashboard");
      else navigate("/profile");
    } catch (err) {
      setError(err.message || "Invalid email or password.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      await register({ name, email, password });
      setSuccess("Account created successfully! Please sign in.");
      switchView("login");
    } catch (err) {
      setError(err.message || "Registration failed.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      const res = await fetch("http://localhost:8000/auth/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Failed to send OTP.");
      }
      setSuccess("OTP sent successfully to your email. Check your inbox or console.");
      setForgotStep("reset");
    } catch (err) {
      setError(err.message || "An error occurred.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      const res = await fetch("http://localhost:8000/auth/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, otp, new_password: password }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Failed to reset password.");
      }
      setSuccess("Password reset successfully! Redirecting to login...");
      setTimeout(() => {
        switchView("login");
      }, 2000);
    } catch (err) {
      setError(err.message || "An error occurred.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const viewConfig = {
    login: {
      title: "Welcome Back",
      subtitle: "Sign in to continue searching jobs and generating tailored resumes.",
      buttonLabel: "Sign In",
      onSubmit: handleLogin,
    },
    signup: {
      title: "Create Account",
      subtitle: "Join JobPilot AI and start your AI-powered career journey.",
      buttonLabel: "Create Account",
      onSubmit: handleSignup,
    },
    forgot: {
      title: forgotStep === "request" ? "Reset Password" : "Enter Verification OTP",
      subtitle: forgotStep === "request" 
        ? "Enter your email and we'll send you a 6-digit OTP to reset your password." 
        : "Enter the OTP sent to your email and your new password to verify.",
      buttonLabel: forgotStep === "request" ? "Send OTP" : "Reset Password",
      onSubmit: forgotStep === "request" ? handleForgotPassword : handleResetPassword,
    },
  };

  const cfg = viewConfig[view];

  return (
    <main className="flex min-h-screen bg-jp-bg-app">
      {/* ========== Left Side: Form ========== */}
      <div className="flex flex-col w-full md:w-[45%] xl:w-[40%] bg-jp-bg-surface/80 backdrop-blur-xl border-r border-jp-border-subtle p-8 md:p-12 lg:p-16 justify-center relative z-10">
        
        <div className="w-full max-w-sm mx-auto space-y-8">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <Icon name="sparkles" fill className="text-jp-accent text-[28px]" />
            <span className="text-[20px] font-bold text-jp-text-primary tracking-tight">JobPilot AI</span>
          </div>

          {/* Title */}
          <div>
            <h1 className="text-3xl font-semibold text-jp-text-primary tracking-tight">{cfg.title}</h1>
            <p className="text-[14px] text-jp-text-tertiary mt-2">{cfg.subtitle}</p>
          </div>

          {/* Feedback Messages */}
          {error && (
            <div className="p-4 rounded-xl flex items-center gap-3 bg-jp-error-muted/30 border border-jp-error/20 text-jp-error">
              <Icon name="error" className="text-[20px] shrink-0" />
              <span className="text-[13px] font-medium leading-tight">{error}</span>
            </div>
          )}
          {success && (
            <div className="p-4 rounded-xl flex items-center gap-3 bg-jp-success-muted/30 border border-jp-success/20 text-jp-success">
              <Icon name="check_circle" className="text-[20px] shrink-0" />
              <span className="text-[13px] font-medium leading-tight">{success}</span>
            </div>
          )}

          {/* Form */}
          <form className="space-y-5" onSubmit={cfg.onSubmit}>
            {/* Name */}
            {view === "signup" && (
              <div>
                <label className="block text-[13px] font-medium text-jp-text-secondary mb-1.5" htmlFor="name">Full Name</label>
                <input
                  id="name"
                  type="text"
                  required
                  placeholder="Jane Doe"
                  className="w-full px-4 py-3 rounded-xl border border-jp-border bg-jp-bg-raised text-[14px] text-jp-text-primary placeholder:text-jp-text-muted focus:border-jp-accent focus:outline-none transition-colors"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
            )}

            {/* Email */}
            <div>
              <label className="block text-[13px] font-medium text-jp-text-secondary mb-1.5" htmlFor="email">Email Address</label>
              <input
                id="email"
                type="email"
                required
                disabled={view === "forgot" && forgotStep === "reset"}
                placeholder="name@company.com"
                className="w-full px-4 py-3 rounded-xl border border-jp-border bg-jp-bg-raised text-[14px] text-jp-text-primary placeholder:text-jp-text-muted focus:border-jp-accent focus:outline-none transition-colors disabled:opacity-50"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            {/* OTP Verification (Step 2 of Forgot Password) */}
            {view === "forgot" && forgotStep === "reset" && (
              <div>
                <label className="block text-[13px] font-medium text-jp-text-secondary mb-1.5" htmlFor="otp">Verification OTP</label>
                <input
                  id="otp"
                  type="text"
                  required
                  maxLength={6}
                  placeholder="123456"
                  className="w-full px-4 py-3 rounded-xl border border-jp-border bg-jp-bg-raised text-[14px] text-jp-text-primary placeholder:text-jp-text-muted focus:border-jp-accent focus:outline-none transition-colors"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                />
              </div>
            )}

            {/* Password */}
            {(view !== "forgot" || (view === "forgot" && forgotStep === "reset")) && (
              <div>
                <div className="flex justify-between items-center mb-1.5">
                  <label className="text-[13px] font-medium text-jp-text-secondary" htmlFor="password">
                    {view === "forgot" ? "New Password" : "Password"}
                  </label>
                  {view === "login" && (
                    <button type="button" className="text-[12px] font-medium text-jp-accent hover:text-jp-accent-hover transition-colors" onClick={() => switchView("forgot")}>
                      Forgot Password?
                    </button>
                  )}
                </div>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    required
                    placeholder="••••••••"
                    className="w-full pl-4 pr-12 py-3 rounded-xl border border-jp-border bg-jp-bg-raised text-[14px] text-jp-text-primary placeholder:text-jp-text-muted focus:border-jp-accent focus:outline-none transition-colors"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center text-jp-text-muted hover:text-jp-text-primary transition-colors"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    <Icon name={showPassword ? "visibility_off" : "visibility"} className="text-[20px]" />
                  </button>
                </div>
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full jp-btn jp-btn-primary py-3 justify-center text-[14px] rounded-xl"
            >
              {isSubmitting ? (
                <>
                  <Icon name="progress_activity" className="text-[18px] animate-spin" />
                  Please wait...
                </>
              ) : (
                <>
                  {cfg.buttonLabel}
                  <Icon name="arrow_forward" className="text-[18px]" />
                </>
              )}
            </button>

            {/* OAuth */}
            {view !== "forgot" && (
              <>
                <div className="flex items-center gap-4 py-2">
                  <div className="flex-1 h-px bg-jp-border-subtle" />
                  <span className="text-[11px] font-semibold text-jp-text-muted uppercase tracking-wider">OR</span>
                  <div className="flex-1 h-px bg-jp-border-subtle" />
                </div>
                <button
                  type="button"
                  className="w-full px-4 py-3 rounded-xl border border-jp-border bg-jp-bg-surface hover:bg-jp-bg-raised flex items-center justify-center gap-3 text-[14px] font-medium text-jp-text-primary transition-colors"
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"></path>
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"></path>
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"></path>
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"></path>
                  </svg>
                  Continue with Google
                </button>
              </>
            )}
          </form>

          {/* Footer Links */}
          <div className="text-center">
            {view === "login" && (
              <p className="text-[13px] text-jp-text-secondary">
                Don't have an account?{" "}
                <button type="button" className="text-jp-accent font-medium hover:text-jp-accent-hover transition-colors" onClick={() => switchView("signup")}>
                  Create Account
                </button>
              </p>
            )}
            {view === "signup" && (
              <p className="text-[13px] text-jp-text-secondary">
                Already have an account?{" "}
                <button type="button" className="text-jp-accent font-medium hover:text-jp-accent-hover transition-colors" onClick={() => switchView("login")}>
                  Sign In
                </button>
              </p>
            )}
            {view === "forgot" && (
              <p className="text-[13px] text-jp-text-secondary">
                Remember your password?{" "}
                <button type="button" className="text-jp-accent font-medium hover:text-jp-accent-hover transition-colors" onClick={() => switchView("login")}>
                  Back to Sign In
                </button>
              </p>
            )}
          </div>
        </div>
      </div>

      {/* ========== Right Side: Showcase ========== */}
      <div className="hidden md:flex flex-col flex-1 bg-jp-bg-inset relative overflow-hidden justify-center items-center p-12">
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-jp-accent/10 rounded-full blur-[100px] pointer-events-none" />
        
        <div className="max-w-2xl relative z-10 w-full space-y-12">
          <div>
            <h2 className="text-4xl font-semibold text-jp-text-primary mb-4 tracking-tight">AI-Powered Career Growth</h2>
            <p className="text-[16px] text-jp-text-secondary leading-relaxed">
              Unlock the power of artificial intelligence to accelerate your career. Search intelligently, tailor resumes instantly, and stand out.
            </p>
          </div>
          
          <div className="grid grid-cols-2 gap-6">
            {[
              { icon: "search", title: "Smart Search", desc: "Real-time indexing filtered by your professional DNA." },
              { icon: "analytics", title: "Match Scoring", desc: "Instantly see how well your profile aligns with job descriptions." },
              { icon: "bolt", title: "Skill Analysis", desc: "Identify critical skill gaps to secure high-impact roles." },
              { icon: "edit_document", title: "Resume Tailoring", desc: "One-click AI optimizations to boost ATS compliance." },
            ].map(item => (
              <div key={item.title} className="jp-card p-6">
                <div className="w-12 h-12 rounded-xl bg-jp-bg-raised border border-jp-border flex items-center justify-center mb-4">
                  <Icon name={item.icon} className="text-[24px] text-jp-accent" />
                </div>
                <h3 className="text-[15px] font-semibold text-jp-text-primary mb-2">{item.title}</h3>
                <p className="text-[13px] text-jp-text-tertiary leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>

          <div className="flex items-center gap-8 pt-8 border-t border-jp-border-subtle">
            <div className="flex -space-x-3">
              <div className="w-10 h-10 rounded-full border-2 border-jp-bg-inset bg-jp-accent flex items-center justify-center text-white font-semibold text-[12px]">AI</div>
              <div className="w-10 h-10 rounded-full border-2 border-jp-bg-inset bg-jp-success flex items-center justify-center text-white font-semibold text-[12px]">ML</div>
              <div className="w-10 h-10 rounded-full border-2 border-jp-bg-inset bg-jp-warning flex items-center justify-center text-white font-semibold text-[12px]">ATS</div>
            </div>
            <p className="text-[13px] font-medium text-jp-text-secondary">
              Trusted by professionals at top-tier tech companies.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}

export default Auth;
