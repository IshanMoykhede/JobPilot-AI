import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';

function Auth() {
  // "login" | "signup" | "forgot"
  const [view, setView] = useState("login");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form fields
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

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
    setShowPassword(false);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      const { hasProfile } = await login({ email, password });
      if (hasProfile) {
        navigate("/dashboard");
      } else {
        navigate("/profile");
      }
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
    setSuccess("If this email is registered, you'll receive a password reset link shortly.");
  };

  /* ---------- Title / subtitle per view ---------- */
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
      title: "Reset Password",
      subtitle: "Enter your email and we'll send you a link to reset your password.",
      buttonLabel: "Send Reset Link",
      onSubmit: handleForgotPassword,
    },
  };

  const cfg = viewConfig[view];

  return (
    <>
      <Header />
      <main className="flex min-h-screen flex-col md:flex-row">
        {/* ========== Left Side: Form ========== */}
        <div className="flex flex-col w-full md:w-[45%] xl:w-[40%] bg-surface-container-lowest px-margin md:px-3xl py-xl md:py-3xl min-h-screen relative z-10">
          {/* Logo */}
          <div className="mb-3xl">
            <div className="flex items-center gap-xs">
              <img alt="JobPilot AI Logo" className="w-8 h-8 object-contain" src="https://lh3.googleusercontent.com/aida/AP1WRLv0-zrysfExadzID741iTQSs4XDmG0OEvLtyvXx5YwR18W1KEz4jyoaa16VuHOYeWZUd5wuXFM9HDStZvne2zsCbaKbkaB0y-xTocGTs4F4gMavnY5D80BT-CiG06xamXK5rVP-xBmP9gyfnl0_9HUI6nUe2tOdZ4G7gZVRQ_DG_9kctRKTmWDrDNQhigbxAQ5ojrqI3da1xEA1RK_x8FkG8dNc-nJVMYUXlHPiR6fmoDIQuRx-MO8fMTpG" />
              <span className="font-headline-md text-headline-md font-bold text-primary">JobPilot AI</span>
            </div>
          </div>

          {/* Title */}
          <div className="mb-xl">
            <h1 className="font-headline-xl text-headline-xl text-on-background mb-xs tracking-tight">{cfg.title}</h1>
            <p className="font-body-md text-body-md text-on-surface-variant">{cfg.subtitle}</p>
          </div>

          {/* Feedback Messages */}
          {error && (
            <div className="mb-lg px-md py-sm rounded-lg flex items-center gap-xs text-error" style={{ backgroundColor: "rgba(186,26,26,0.08)" }}>
              <span className="material-symbols-outlined text-[18px]">error</span>
              <span className="font-body-sm text-body-sm font-medium">{error}</span>
            </div>
          )}
          {success && (
            <div className="mb-lg px-md py-sm rounded-lg flex items-center gap-xs" style={{ backgroundColor: "rgba(0,84,121,0.08)", color: "#005479" }}>
              <span className="material-symbols-outlined text-[18px]">check_circle</span>
              <span className="font-body-sm text-body-sm font-medium">{success}</span>
            </div>
          )}

          {/* Form */}
          <form className="space-y-lg flex-grow" onSubmit={cfg.onSubmit}>
            {/* Name (Sign Up only) */}
            {view === "signup" && (
              <div>
                <label className="block font-label-md text-label-md text-on-surface mb-xs" htmlFor="name">Full Name</label>
                <input
                  className="w-full px-md py-sm rounded-lg border border-outline-variant bg-surface-container-lowest font-body-md text-body-md form-input-focus transition-all"
                  id="name"
                  placeholder="Jane Doe"
                  required
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
            )}

            {/* Email (all views) */}
            <div>
              <label className="block font-label-md text-label-md text-on-surface mb-xs" htmlFor="email">Email Address</label>
              <input
                className="w-full px-md py-sm rounded-lg border border-outline-variant bg-surface-container-lowest font-body-md text-body-md form-input-focus transition-all"
                id="email"
                placeholder="name@company.com"
                required
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            {/* Password (login + signup only) */}
            {view !== "forgot" && (
              <div className="relative">
                <div className="flex justify-between items-center mb-xs">
                  <label className="block font-label-md text-label-md text-on-surface" htmlFor="password">Password</label>
                  {view === "login" && (
                    <button
                      type="button"
                      className="font-label-sm text-label-sm text-primary hover:underline transition-colors"
                      onClick={() => switchView("forgot")}
                    >
                      Forgot Password?
                    </button>
                  )}
                </div>
                <div className="relative">
                  <input
                    className="w-full px-md py-sm rounded-lg border border-outline-variant bg-surface-container-lowest font-body-md text-body-md form-input-focus transition-all pr-12"
                    id="password"
                    placeholder="••••••••"
                    required
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <button
                    className="absolute right-md top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-on-surface transition-colors"
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    <span className="material-symbols-outlined">{showPassword ? "visibility_off" : "visibility"}</span>
                  </button>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <button
              className="w-full bg-primary-container text-on-primary font-label-md text-label-md py-md rounded-lg shadow-sm hover:brightness-110 active:scale-[0.98] transition-all flex justify-center items-center gap-xs disabled:opacity-60 disabled:cursor-not-allowed"
              type="submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <span className="material-symbols-outlined text-[18px] animate-spin">progress_activity</span>
                  Please wait...
                </>
              ) : (
                <>
                  {cfg.buttonLabel}
                  <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                </>
              )}
            </button>

            {/* Google OAuth (login + signup only) */}
            {view !== "forgot" && (
              <>
                <div className="flex items-center gap-md py-xs">
                  <div className="flex-grow h-px bg-outline-variant"></div>
                  <span className="font-label-sm text-label-sm text-outline">OR</span>
                  <div className="flex-grow h-px bg-outline-variant"></div>
                </div>
                <button className="w-full flex items-center justify-center gap-sm px-md py-md rounded-lg border border-outline-variant bg-surface-container-lowest hover:bg-surface-container transition-colors font-label-md text-label-md" type="button">
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
          <div className="mt-xl text-center">
            {view === "login" && (
              <p className="font-body-sm text-body-sm text-on-surface-variant">
                Don&apos;t have an account?{" "}
                <button type="button" className="text-primary font-bold hover:underline transition-colors" onClick={() => switchView("signup")}>
                  Create Account
                </button>
              </p>
            )}
            {view === "signup" && (
              <p className="font-body-sm text-body-sm text-on-surface-variant">
                Already have an account?{" "}
                <button type="button" className="text-primary font-bold hover:underline transition-colors" onClick={() => switchView("login")}>
                  Sign In
                </button>
              </p>
            )}
            {view === "forgot" && (
              <p className="font-body-sm text-body-sm text-on-surface-variant">
                Remember your password?{" "}
                <button type="button" className="text-primary font-bold hover:underline transition-colors" onClick={() => switchView("login")}>
                  Back to Sign In
                </button>
              </p>
            )}
          </div>
        </div>

        {/* ========== Right Side: Capability Showcase ========== */}
        <div className="hidden md:flex flex-col w-full md:w-[55%] xl:w-[60%] bg-surface-container relative overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-primary/10 via-transparent to-transparent"></div>
          <div className="relative z-10 flex flex-col h-full px-2xl py-3xl max-w-4xl mx-auto">
            <div className="mb-2xl">
              <h2 className="font-headline-xl text-headline-xl text-on-background mb-sm tracking-tight">What You&apos;ll Be Able To Do</h2>
              <p className="font-body-lg text-body-lg text-on-surface-variant max-w-lg">Unlock the power of artificial intelligence to accelerate your career growth with surgical precision.</p>
            </div>
            {/* Bento Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-lg flex-grow">
              <div className="glass-card p-xl rounded-xl group hover:-translate-y-1 transition-transform duration-300">
                <div className="w-12 h-12 rounded-lg bg-surface-container-highest flex items-center justify-center text-primary mb-md group-hover:bg-primary group-hover:text-on-primary transition-colors">
                  <span className="material-symbols-outlined">search</span>
                </div>
                <h3 className="font-headline-sm text-headline-sm mb-xs">Search Jobs</h3>
                <p className="font-body-sm text-body-sm text-on-surface-variant">Real-time indexing of thousands of boards filtered by your unique professional DNA.</p>
              </div>
              <div className="glass-card p-xl rounded-xl group hover:-translate-y-1 transition-transform duration-300">
                <div className="w-12 h-12 rounded-lg bg-surface-container-highest flex items-center justify-center text-tertiary mb-md group-hover:bg-tertiary group-hover:text-on-tertiary transition-colors">
                  <span className="material-symbols-outlined">analytics</span>
                </div>
                <h3 className="font-headline-sm text-headline-sm mb-xs">Resume Matching</h3>
                <p className="font-body-sm text-body-sm text-on-surface-variant">Instantly see how well your profile matches any job description with high-accuracy scores.</p>
              </div>
              <div className="glass-card p-xl rounded-xl group hover:-translate-y-1 transition-transform duration-300">
                <div className="w-12 h-12 rounded-lg bg-surface-container-highest flex items-center justify-center text-secondary mb-md group-hover:bg-secondary group-hover:text-on-secondary transition-colors">
                  <span className="material-symbols-outlined">bolt</span>
                </div>
                <h3 className="font-headline-sm text-headline-sm mb-xs">Skill Gap Analysis</h3>
                <p className="font-body-sm text-body-sm text-on-surface-variant">Identify specific skills to acquire or emphasize to secure your next high-impact role.</p>
              </div>
              <div className="glass-card p-xl rounded-xl group hover:-translate-y-1 transition-transform duration-300">
                <div className="w-12 h-12 rounded-lg bg-surface-container-highest flex items-center justify-center text-primary mb-md group-hover:bg-primary group-hover:text-on-primary transition-colors">
                  <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>magic_button</span>
                </div>
                <h3 className="font-headline-sm text-headline-sm mb-xs">Resume Tailoring</h3>
                <p className="font-body-sm text-body-sm text-on-surface-variant">One-click AI optimizations that reorganize your experience for maximum ATS compliance.</p>
              </div>
            </div>
            {/* Trust Section */}
            <div className="mt-2xl pt-xl border-t border-outline-variant flex flex-col sm:flex-row gap-lg items-center justify-between">
              <div className="flex items-center gap-sm">
                <div className="flex -space-x-2">
                  <div className="w-8 h-8 rounded-full border-2 border-surface-container-lowest bg-surface-dim"></div>
                  <div className="w-8 h-8 rounded-full border-2 border-surface-container-lowest bg-primary-fixed"></div>
                  <div className="w-8 h-8 rounded-full border-2 border-surface-container-lowest bg-secondary-fixed"></div>
                </div>
                <span className="font-label-sm text-label-sm text-on-surface-variant">Trusted by 10k+ professionals</span>
              </div>
              <div className="flex flex-wrap gap-md justify-center">
                <div className="flex items-center gap-xs font-label-sm text-label-sm text-on-surface">
                  <span className="material-symbols-outlined text-[16px] text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                  Secure Storage
                </div>
                <div className="flex items-center gap-xs font-label-sm text-label-sm text-on-surface">
                  <span className="material-symbols-outlined text-[16px] text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                  AI Tailoring
                </div>
                <div className="flex items-center gap-xs font-label-sm text-label-sm text-on-surface">
                  <span className="material-symbols-outlined text-[16px] text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                  Personalized
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}

export default Auth;
