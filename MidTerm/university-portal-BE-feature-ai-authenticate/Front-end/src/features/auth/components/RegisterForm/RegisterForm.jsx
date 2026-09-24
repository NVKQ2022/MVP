import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Label } from '@/components/ui/label/label';
import { Input } from '@/components/ui/input/input';
import { Button } from '@/components/ui/button/button';
import { Alert, AlertDescription } from '@/components/ui/alert/alert';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { isValidEmail, getPasswordStrengthError } from '@/utils/validators';

import './RegisterForm.scss';

export function RegisterForm() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (field) => (e) => {
    setForm((prev) => ({
      ...prev,
      [field]: e.target.value,
    }));
  };

  const validate = () => {
    if (!form.name.trim()) {
      return 'Please enter your full name.';
    }

    if (!isValidEmail(form.email)) {
      return 'Please enter a valid email address.';
    }

    const passwordError = getPasswordStrengthError(form.password);

    if (passwordError) {
      return passwordError;
    }

    if (form.password !== form.confirmPassword) {
      return 'Passwords do not match.';
    }

    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    const validationError = validate();

    if (validationError) {
      setError(validationError);
      return;
    }

    setSubmitting(true);

    try {
      await register({
        name: form.name,
        email: form.email,
        password: form.password,
      });

      navigate('/verify-email', {
        replace: true,
        state: {
          email: form.email,
        },
      });
    } catch (err) {
      const status = err?.response?.status;

      if (status === 409) {
        setError('An account with this email already exists.');
      } else if (status === 403) {
        setError('This email is not authorized to register. Contact your administrator.');
      } else {
        setError('Something went wrong. Please try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="register-form">
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="register-form__field">
        <Label htmlFor="name">Full Name</Label>

        <Input id="name" value={form.name} onChange={handleChange('name')} required />
      </div>

      <div className="register-form__field">
        <Label htmlFor="email">Email</Label>

        <Input
          id="email"
          type="email"
          value={form.email}
          onChange={handleChange('email')}
          required
        />
      </div>

      <div className="register-form__field">
        <Label htmlFor="password">Password</Label>

        <Input
          id="password"
          type="password"
          value={form.password}
          onChange={handleChange('password')}
          required
        />

        <p className="register-form__hint">
          At least 8 characters, one uppercase letter, one number.
        </p>
      </div>

      <div className="register-form__field">
        <Label htmlFor="confirmPassword">Confirm Password</Label>

        <Input
          id="confirmPassword"
          type="password"
          value={form.confirmPassword}
          onChange={handleChange('confirmPassword')}
          required
        />
      </div>

      <Button type="submit" className="register-form__submit" disabled={submitting}>
        {submitting ? 'Creating account...' : 'Create Account'}
      </Button>
    </form>
  );
}
