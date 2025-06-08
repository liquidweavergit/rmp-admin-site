// Validation utilities for authentication forms

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

export const validateEmail = (email: string): ValidationResult => {
  const errors: string[] = [];

  if (!email) {
    errors.push("Email is required");
  } else {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      errors.push("Please enter a valid email address");
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

export const validatePassword = (password: string): ValidationResult => {
  const errors: string[] = [];

  if (!password) {
    errors.push("Password is required");
  } else {
    if (password.length < 8) {
      errors.push("Password must be at least 8 characters long");
    }

    if (password.length > 128) {
      errors.push("Password must be no more than 128 characters long");
    }

    const hasUpper = /[A-Z]/.test(password);
    const hasLower = /[a-z]/.test(password);
    const hasDigit = /\d/.test(password);

    if (!hasUpper || !hasLower || !hasDigit) {
      errors.push(
        "Password must contain at least one uppercase letter, one lowercase letter, and one digit",
      );
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

export const validateName = (name: string, fieldName: string): ValidationResult => {
  const errors: string[] = [];

  if (!name || name.trim().length === 0) {
    errors.push(`${fieldName} is required`);
  } else {
    if (name.trim().length > 100) {
      errors.push(`${fieldName} must be no more than 100 characters long`);
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

export const validatePhone = (phone: string): ValidationResult => {
  const errors: string[] = [];

  if (phone && phone.trim() !== "") {
    // Remove non-digit characters for validation
    const digitsOnly = phone.replace(/\D/g, "");

    if (digitsOnly.length < 10) {
      errors.push("Phone number must have at least 10 digits");
    } else if (digitsOnly.length > 15) {
      errors.push("Phone number must be no more than 15 digits");
    }

    if (phone.length > 20) {
      errors.push("Phone number must be no more than 20 characters long (including formatting)");
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

export const validatePasswordConfirmation = (
  password: string,
  confirmPassword: string,
): ValidationResult => {
  const errors: string[] = [];

  if (!confirmPassword) {
    errors.push("Please confirm your password");
  } else if (password !== confirmPassword) {
    errors.push("Passwords do not match");
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

// Combined validation for registration form
export interface RegisterFormData {
  email: string;
  password: string;
  confirmPassword: string;
  first_name: string;
  last_name: string;
  phone?: string;
}

export const validateRegisterForm = (
  data: RegisterFormData,
): { isValid: boolean; fieldErrors: Record<string, string[]> } => {
  const fieldErrors: Record<string, string[]> = {};

  const emailValidation = validateEmail(data.email);
  if (!emailValidation.isValid) {
    fieldErrors.email = emailValidation.errors;
  }

  const passwordValidation = validatePassword(data.password);
  if (!passwordValidation.isValid) {
    fieldErrors.password = passwordValidation.errors;
  }

  const confirmPasswordValidation = validatePasswordConfirmation(
    data.password,
    data.confirmPassword,
  );
  if (!confirmPasswordValidation.isValid) {
    fieldErrors.confirmPassword = confirmPasswordValidation.errors;
  }

  const firstNameValidation = validateName(data.first_name, "First name");
  if (!firstNameValidation.isValid) {
    fieldErrors.first_name = firstNameValidation.errors;
  }

  const lastNameValidation = validateName(data.last_name, "Last name");
  if (!lastNameValidation.isValid) {
    fieldErrors.last_name = lastNameValidation.errors;
  }

  if (data.phone) {
    const phoneValidation = validatePhone(data.phone);
    if (!phoneValidation.isValid) {
      fieldErrors.phone = phoneValidation.errors;
    }
  }

  return {
    isValid: Object.keys(fieldErrors).length === 0,
    fieldErrors,
  };
};

// Combined validation for login form
export interface LoginFormData {
  email: string;
  password: string;
}

export const validateLoginForm = (
  data: LoginFormData,
): { isValid: boolean; fieldErrors: Record<string, string[]> } => {
  const fieldErrors: Record<string, string[]> = {};

  const emailValidation = validateEmail(data.email);
  if (!emailValidation.isValid) {
    fieldErrors.email = emailValidation.errors;
  }

  if (!data.password) {
    fieldErrors.password = ["Password is required"];
  }

  return {
    isValid: Object.keys(fieldErrors).length === 0,
    fieldErrors,
  };
};
