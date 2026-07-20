import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Icon from '../components/common/Icon';

const LiveProductExperience = () => {
  const [step, setStep] = useState(0);
  const [score, setScore] = useState(0);
  
  useEffect(() => {
    let timers = [];
    const runSequence = () => {
      setStep(0);
      setScore(0);
      timers.push(setTimeout(() => setStep(1), 1000));
      timers.push(setTimeout(() => setStep(2), 2500));
      timers.push(setTimeout(() => setStep(3), 4000));
      timers.push(setTimeout(() => setStep(4), 5500));
      timers.push(setTimeout(() => {
        setStep(5);
        let currentScore = 0;
        const interval = setInterval(() => {
          currentScore += 4;
          if (currentScore >= 96) {
            setScore(96);
            clearInterval(interval);
          } else {
            setScore(currentScore);
          }
        }, 30);
        timers.push(interval);
      }, 7000));
      // Loop the animation
      timers.push(setTimeout(runSequence, 12000));
    };
    
    runSequence();
    
    return () => timers.forEach(t => { clearTimeout(t); clearInterval(t); });
  }, []);

  return (
    <div className="w-full max-w-2xl bg-jp-bg-surface/60 backdrop-blur-2xl border border-jp-border-subtle rounded-3xl shadow-[0_30px_100px_rgba(0,0,0,0.6)] overflow-hidden relative flex flex-col h-[500px] ring-1 ring-white/5 mx-auto">
      {/* Header */}
      <div className="h-12 border-b border-jp-border-subtle/50 flex items-center px-6 gap-3 bg-jp-bg-app/50">
        <div className="w-3 h-3 rounded-full bg-jp-error/80"></div>
        <div className="w-3 h-3 rounded-full bg-jp-warning/80"></div>
        <div className="w-3 h-3 rounded-full bg-jp-success/80"></div>
        <div className="mx-auto text-[12px] font-mono text-jp-text-tertiary tracking-wider">jobpilot-engine.exe</div>
      </div>
      
      {/* Body */}
      <div className="flex-1 p-8 md:p-12 flex flex-col gap-8 font-mono text-[14px] md:text-[15px] relative overflow-hidden">
        
        {/* Glow behind the terminal */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-jp-accent/10 blur-[80px] rounded-full pointer-events-none z-0"></div>
        
        {/* Typing */}
        <div className={`relative z-10 flex items-center gap-3 transition-all duration-500 ${step >= 1 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <Icon name="search" className="text-jp-accent text-[16px]" />
          <span className="text-jp-text-secondary">Searching Google Jobs for <span className="text-white">Senior Frontend Engineer</span>...</span>
        </div>

        {/* Reading */}
        <div className={`relative z-10 flex flex-col gap-3 transition-all duration-500 delay-100 ${step >= 2 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <div className="flex items-center justify-between">
            <span className="text-jp-text-primary flex items-center gap-3"><Icon name="description" className="text-blue-400 text-[18px]"/> Reading resume.pdf</span>
            <span className="text-jp-text-tertiary">{step > 2 ? '100%' : 'Parsing...'}</span>
          </div>
          <div className="h-[4px] w-full bg-jp-bg-raised rounded-full overflow-hidden mt-1">
            <div className={`h-full bg-blue-400 transition-all duration-[1200ms] ease-out ${step >= 2 ? 'w-full' : 'w-0'}`}></div>
          </div>
        </div>

        {/* Matching */}
        <div className={`relative z-10 flex flex-col gap-3 transition-all duration-500 delay-100 ${step >= 3 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <div className="flex items-center justify-between">
            <span className="text-jp-text-primary flex items-center gap-3"><Icon name="radar" className="text-jp-accent text-[18px]"/> Semantic Matching</span>
            <span className="text-jp-text-tertiary">{step > 3 ? 'Complete' : 'Processing...'}</span>
          </div>
          <div className="h-[4px] w-full bg-jp-bg-raised rounded-full overflow-hidden mt-1">
            <div className={`h-full bg-jp-accent transition-all duration-[1200ms] ease-out ${step >= 3 ? 'w-full' : 'w-0'}`}></div>
          </div>
        </div>

        {/* Tailoring */}
        <div className={`relative z-10 flex flex-col gap-2 transition-all duration-500 delay-100 ${step >= 4 ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <div className="flex items-center justify-between">
            <span className="text-jp-text-primary flex items-center gap-2"><Icon name="auto_awesome" className="text-purple-400 text-[16px]"/> Auto-Tailoring</span>
            <span className="text-jp-text-tertiary">{step > 4 ? 'Complete' : 'Optimizing...'}</span>
          </div>
          <div className="h-[4px] w-full bg-jp-bg-raised rounded-full overflow-hidden mt-1">
            <div className={`h-full bg-purple-400 transition-all duration-[1200ms] ease-out ${step >= 4 ? 'w-full' : 'w-0'}`}></div>
          </div>
        </div>

        {/* Results overlay */}
        <div className={`absolute bottom-8 left-8 right-8 bg-jp-bg-app border border-jp-border-subtle rounded-2xl p-6 flex justify-around items-center shadow-2xl transition-all duration-700 ease-out z-20 backdrop-blur-md ${step >= 5 ? 'opacity-100 translate-y-0 scale-100' : 'opacity-0 translate-y-8 scale-95 pointer-events-none'}`}>
           <div className="text-center font-sans">
             <div className="text-[48px] font-extrabold text-transparent bg-clip-text bg-gradient-to-br from-jp-success to-emerald-400 leading-none">{score}%</div>
             <div className="text-[12px] font-bold uppercase tracking-widest text-jp-text-secondary mt-2">Match Score</div>
           </div>
           <div className="w-px h-20 bg-jp-border-subtle"></div>
           <div className="text-center font-sans">
             <div className="text-[48px] font-extrabold text-transparent bg-clip-text bg-gradient-to-br from-blue-400 to-indigo-400 leading-none">{score > 0 ? score - 2 : 0}%</div>
             <div className="text-[12px] font-bold uppercase tracking-widest text-jp-text-secondary mt-2">ATS Score</div>
           </div>
        </div>

      </div>
    </div>
  );
};

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
      setSuccess("OTP sent successfully to your email.");
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
      subtitle: "Your AI career copilot is ready.",
      buttonLabel: "Sign In",
      onSubmit: handleLogin,
    },
    signup: {
      title: "Stop Guessing.",
      subtitle: "Start matching. Land better jobs with AI.",
      buttonLabel: "Create Account",
      onSubmit: handleSignup,
    },
    forgot: {
      title: forgotStep === "request" ? "Reset Password" : "Enter Verification OTP",
      subtitle: forgotStep === "request" 
        ? "Enter your email to receive a secure recovery code." 
        : "Enter the code sent to your email and a new password.",
      buttonLabel: forgotStep === "request" ? "Send Code" : "Reset Password",
      onSubmit: forgotStep === "request" ? handleForgotPassword : handleResetPassword,
    },
  };

  const cfg = viewConfig[view];

  return (
    <main className="flex min-h-screen bg-jp-bg-app relative overflow-hidden">
      
      {/* ========== Left Side: Form ========== */}
      <div className="flex flex-col w-full md:w-[45%] xl:w-[40%] bg-jp-bg-app relative z-10 p-8 md:p-12 lg:p-16 justify-center shadow-[20px_0_60px_rgba(0,0,0,0.5)]">
        
        {/* Subtle Left Side Glow */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-[-20%] left-[-20%] w-[600px] h-[600px] bg-jp-accent/5 rounded-full blur-[120px]"></div>
        </div>

        <div className="w-full max-w-[420px] mx-auto space-y-10 animate-fade-in relative z-10">
          {/* Logo & Branding */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/')}>
            <img src="/logo.png" alt="JobPilot Logo" className="w-10 h-10 rounded-xl shadow-[0_0_15px_var(--color-jp-accent-glow)]" />
            <span className="text-[22px] font-bold text-jp-text-primary tracking-tight">JobPilot AI</span>
          </div>

          {/* Title Area */}
          <div>
            <h1 className="text-[32px] font-bold text-jp-text-primary tracking-tight leading-tight">{cfg.title}</h1>
            <p className="text-[15px] text-jp-text-secondary mt-2">{cfg.subtitle}</p>
          </div>

          {/* Feedback Messages */}
          {error && (
            <div className="p-4 rounded-xl flex items-center gap-3 bg-jp-error-muted/30 border border-jp-error/20 text-jp-error animate-slide-up">
              <Icon name="error" className="text-[18px] shrink-0" />
              <span className="text-[13px] font-medium leading-snug">{error}</span>
            </div>
          )}
          {success && (
            <div className="p-4 rounded-xl flex items-center gap-3 bg-jp-success-muted/30 border border-jp-success/20 text-jp-success animate-slide-up">
              <Icon name="check_circle" className="text-[18px] shrink-0" />
              <span className="text-[13px] font-medium leading-snug">{success}</span>
            </div>
          )}

          {/* Form */}
          <form className="space-y-4" onSubmit={cfg.onSubmit}>
            {/* Name */}
            {view === "signup" && (
              <div>
                <label className="block text-[12px] font-semibold uppercase tracking-wider text-jp-text-tertiary mb-1.5" htmlFor="name">Full Name</label>
                <input
                  id="name"
                  type="text"
                  required
                  placeholder="Jane Doe"
                  className="w-full px-4 py-3 rounded-xl border border-jp-border-subtle bg-jp-bg-surface text-[14px] text-jp-text-primary placeholder:text-jp-text-muted focus:border-jp-accent focus:ring-2 focus:ring-jp-accent/20 focus:outline-none transition-all"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
            )}

            {/* Email */}
            <div>
              <label className="block text-[12px] font-semibold uppercase tracking-wider text-jp-text-tertiary mb-1.5" htmlFor="email">Email Address</label>
              <input
                id="email"
                type="email"
                required
                disabled={view === "forgot" && forgotStep === "reset"}
                placeholder="name@company.com"
                className="w-full px-4 py-3 rounded-xl border border-jp-border-subtle bg-jp-bg-surface text-[14px] text-jp-text-primary placeholder:text-jp-text-muted focus:border-jp-accent focus:ring-2 focus:ring-jp-accent/20 focus:outline-none transition-all disabled:opacity-50"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            {/* OTP Verification */}
            {view === "forgot" && forgotStep === "reset" && (
              <div>
                <label className="block text-[12px] font-semibold uppercase tracking-wider text-jp-text-tertiary mb-1.5" htmlFor="otp">Verification Code</label>
                <input
                  id="otp"
                  type="text"
                  required
                  maxLength={6}
                  placeholder="123456"
                  className="w-full px-4 py-3 rounded-xl border border-jp-border-subtle bg-jp-bg-surface text-[14px] text-jp-text-primary tracking-widest font-mono placeholder:text-jp-text-muted placeholder:tracking-normal focus:border-jp-accent focus:ring-2 focus:ring-jp-accent/20 focus:outline-none transition-all"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                />
              </div>
            )}

            {/* Password */}
            {(view !== "forgot" || (view === "forgot" && forgotStep === "reset")) && (
              <div>
                <div className="flex justify-between items-center mb-1.5">
                  <label className="block text-[12px] font-semibold uppercase tracking-wider text-jp-text-tertiary" htmlFor="password">
                    {view === "forgot" ? "New Password" : "Password"}
                  </label>
                  {view === "login" && (
                    <button type="button" className="text-[12px] font-medium text-jp-accent hover:text-jp-accent-hover transition-colors" onClick={() => switchView("forgot")}>
                      Forgot?
                    </button>
                  )}
                </div>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    required
                    placeholder="••••••••"
                    className="w-full pl-4 pr-12 py-3 rounded-xl border border-jp-border-subtle bg-jp-bg-surface text-[14px] text-jp-text-primary placeholder:text-jp-text-muted focus:border-jp-accent focus:ring-2 focus:ring-jp-accent/20 focus:outline-none transition-all"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center text-jp-text-muted hover:text-jp-text-primary transition-colors"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    <Icon name={showPassword ? "visibility_off" : "visibility"} className="text-[18px]" />
                  </button>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <div className="pt-2">
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full py-3.5 px-4 bg-white hover:bg-gray-100 text-black font-bold text-[14px] rounded-xl flex items-center justify-center gap-2 transition-colors disabled:opacity-70 group"
              >
                {isSubmitting ? (
                  <>
                    <Icon name="progress_activity" className="text-[18px] animate-spin" />
                    Please wait...
                  </>
                ) : (
                  <>
                    {cfg.buttonLabel}
                    <Icon name="arrow_forward" className="text-[16px] group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>
            </div>

            {/* OAuth */}
            {view !== "forgot" && (
              <>
                <div className="flex items-center gap-4 py-4">
                  <div className="flex-1 h-px bg-jp-border-subtle" />
                  <span className="text-[10px] font-semibold text-jp-text-tertiary uppercase tracking-widest">Or Continue With</span>
                  <div className="flex-1 h-px bg-jp-border-subtle" />
                </div>
                <button
                  type="button"
                  className="w-full px-4 py-3 rounded-xl border border-jp-border-subtle bg-jp-bg-surface hover:bg-jp-bg-raised flex items-center justify-center gap-3 text-[14px] font-medium text-jp-text-primary transition-colors"
                >
                  <svg className="w-4 h-4" viewBox="0 0 24 24">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"></path>
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"></path>
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"></path>
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"></path>
                  </svg>
                  Google
                </button>
              </>
            )}
          </form>

          {/* Footer Links */}
          <div className="text-center pt-4">
            {view === "login" && (
              <p className="text-[13px] text-jp-text-secondary">
                Don't have an account?{" "}
                <button type="button" className="text-white font-medium hover:underline underline-offset-4" onClick={() => switchView("signup")}>
                  Sign up
                </button>
              </p>
            )}
            {view === "signup" && (
              <p className="text-[13px] text-jp-text-secondary">
                Already have an account?{" "}
                <button type="button" className="text-white font-medium hover:underline underline-offset-4" onClick={() => switchView("login")}>
                  Sign in
                </button>
              </p>
            )}
            {view === "forgot" && (
              <p className="text-[13px] text-jp-text-secondary">
                <button type="button" className="text-white font-medium hover:underline underline-offset-4" onClick={() => switchView("login")}>
                  &larr; Back to sign in
                </button>
              </p>
            )}
          </div>
          
          {/* Trust Row */}
          <div className="flex justify-center items-center gap-4 text-[11px] font-medium text-jp-text-tertiary pt-4">
            <span className="flex items-center gap-1"><Icon name="verified" className="text-[12px]" /> ATS Optimized</span>
            <span className="w-1 h-1 rounded-full bg-jp-border-subtle"></span>
            <span className="flex items-center gap-1"><Icon name="lock" className="text-[12px]" /> Privacy First</span>
          </div>

        </div>
      </div>

      {/* ========== Right Side: Live Product Experience ========== */}
      <div className="hidden md:flex flex-col flex-1 relative items-center justify-center bg-black">
        {/* Immersive Deep Background */}
        <div className="absolute inset-0 bg-grid opacity-10"></div>
        <div className="absolute top-1/4 -right-1/4 w-[800px] h-[800px] bg-jp-accent/10 rounded-full blur-[150px] pointer-events-none mix-blend-screen animate-pulse" style={{ animationDuration: '8s' }}></div>
        <div className="absolute bottom-0 -left-1/4 w-[600px] h-[600px] bg-blue-500/10 rounded-full blur-[150px] pointer-events-none mix-blend-screen animate-pulse" style={{ animationDuration: '10s' }}></div>
        
        <div className="relative z-10 w-full px-12 flex flex-col items-center">
          <div className="mb-12 text-center">
             <h2 className="text-[28px] font-bold text-white mb-2 drop-shadow-lg">Experience the unfair advantage.</h2>
             <p className="text-[15px] text-jp-text-secondary">Watch the JobPilot engine tailor a profile in real-time.</p>
          </div>
          
          <LiveProductExperience />
        </div>
      </div>
    </main>
  );
}

export default Auth;

