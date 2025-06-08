import {
  validateEmail,
  validatePassword,
  validateName,
  validatePhone,
  validatePasswordConfirmation,
  validateRegisterForm,
  validateLoginForm,
} from "../../utils/validation";

describe("Validation Utils", () => {
  describe("validateEmail", () => {
    it("should validate correct email addresses", () => {
      const validEmails = [
        "test@example.com",
        "user.name@domain.co.uk",
        "user+tag@example.org",
        "user123@test-domain.com",
      ];

      validEmails.forEach((email) => {
        const result = validateEmail(email);
        expect(result.isValid).toBe(true);
        expect(result.errors).toHaveLength(0);
      });
    });

    it("should reject invalid email addresses", () => {
      const invalidEmails = [
        "",
        "invalid",
        "invalid@",
        "@invalid.com",
        "invalid.com",
        "invalid@.com",
        "invalid@com.",
        "invalid..email@example.com",
      ];

      invalidEmails.forEach((email) => {
        const result = validateEmail(email);
        expect(result.isValid).toBe(false);
        expect(result.errors.length).toBeGreaterThan(0);
      });
    });

    it("should return appropriate error messages", () => {
      const emptyResult = validateEmail("");
      expect(emptyResult.errors).toContain("Email is required");

      const invalidResult = validateEmail("invalid-email");
      expect(invalidResult.errors).toContain("Please enter a valid email address");
    });
  });

  describe("validatePassword", () => {
    it("should validate strong passwords", () => {
      const validPasswords = ["Password123", "MySecure1Pass", "Complex9Password", "Test123456"];

      validPasswords.forEach((password) => {
        const result = validatePassword(password);
        expect(result.isValid).toBe(true);
        expect(result.errors).toHaveLength(0);
      });
    });

    it("should reject weak passwords", () => {
      const weakPasswords = [
        "",
        "short",
        "password", // no uppercase or digit
        "PASSWORD", // no lowercase or digit
        "12345678", // no letters
        "Password", // no digit
        "password1", // no uppercase
        "PASSWORD1", // no lowercase
      ];

      weakPasswords.forEach((password) => {
        const result = validatePassword(password);
        expect(result.isValid).toBe(false);
        expect(result.errors.length).toBeGreaterThan(0);
      });
    });

    it("should reject passwords that are too long", () => {
      const tooLongPassword = "A".repeat(129) + "1a";
      const result = validatePassword(tooLongPassword);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain("Password must be no more than 128 characters long");
    });

    it("should return appropriate error messages", () => {
      const emptyResult = validatePassword("");
      expect(emptyResult.errors).toContain("Password is required");

      const shortResult = validatePassword("short");
      expect(shortResult.errors).toContain("Password must be at least 8 characters long");

      const weakResult = validatePassword("password");
      expect(weakResult.errors).toContain(
        "Password must contain at least one uppercase letter, one lowercase letter, and one digit",
      );
    });
  });

  describe("validateName", () => {
    it("should validate proper names", () => {
      const validNames = ["John", "Mary-Jane", "José", "O'Connor", "Van Der Berg"];

      validNames.forEach((name) => {
        const result = validateName(name, "First name");
        expect(result.isValid).toBe(true);
        expect(result.errors).toHaveLength(0);
      });
    });

    it("should reject invalid names", () => {
      const invalidNames = ["", "   ", "A".repeat(101)];

      invalidNames.forEach((name) => {
        const result = validateName(name, "First name");
        expect(result.isValid).toBe(false);
        expect(result.errors.length).toBeGreaterThan(0);
      });
    });

    it("should return appropriate error messages with field name", () => {
      const emptyResult = validateName("", "Last name");
      expect(emptyResult.errors).toContain("Last name is required");

      const tooLongResult = validateName("A".repeat(101), "First name");
      expect(tooLongResult.errors).toContain("First name must be no more than 100 characters long");
    });
  });

  describe("validatePhone", () => {
    it("should validate proper phone numbers", () => {
      const validPhones = [
        "+1 (555) 123-4567",
        "5551234567",
        "+44 20 7946 0958",
        "(555) 123-4567",
        "555.123.4567",
      ];

      validPhones.forEach((phone) => {
        const result = validatePhone(phone);
        expect(result.isValid).toBe(true);
        expect(result.errors).toHaveLength(0);
      });
    });

    it("should allow empty phone numbers", () => {
      const result = validatePhone("");
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it("should reject invalid phone numbers", () => {
      const invalidPhones = [
        "123",
        "123456789", // too short
        "12345678901234567890", // too long (digits)
        "A".repeat(21), // too long (characters)
      ];

      invalidPhones.forEach((phone) => {
        const result = validatePhone(phone);
        expect(result.isValid).toBe(false);
        expect(result.errors.length).toBeGreaterThan(0);
      });
    });
  });

  describe("validatePasswordConfirmation", () => {
    it("should validate matching passwords", () => {
      const password = "Password123";
      const result = validatePasswordConfirmation(password, password);
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it("should reject non-matching passwords", () => {
      const result = validatePasswordConfirmation("Password123", "Different123");
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain("Passwords do not match");
    });

    it("should reject empty confirmation", () => {
      const result = validatePasswordConfirmation("Password123", "");
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain("Please confirm your password");
    });
  });

  describe("validateRegisterForm", () => {
    const validFormData = {
      email: "test@example.com",
      password: "Password123",
      confirmPassword: "Password123",
      first_name: "John",
      last_name: "Doe",
      phone: "+1 (555) 123-4567",
    };

    it("should validate complete valid form", () => {
      const result = validateRegisterForm(validFormData);
      expect(result.isValid).toBe(true);
      expect(Object.keys(result.fieldErrors)).toHaveLength(0);
    });

    it("should validate form without phone", () => {
      const formWithoutPhone = { ...validFormData, phone: "" };
      const result = validateRegisterForm(formWithoutPhone);
      expect(result.isValid).toBe(true);
      expect(Object.keys(result.fieldErrors)).toHaveLength(0);
    });

    it("should collect all field errors", () => {
      const invalidFormData = {
        email: "invalid-email",
        password: "weak",
        confirmPassword: "different",
        first_name: "",
        last_name: "A".repeat(101),
        phone: "123",
      };

      const result = validateRegisterForm(invalidFormData);
      expect(result.isValid).toBe(false);
      expect(result.fieldErrors.email).toBeDefined();
      expect(result.fieldErrors.password).toBeDefined();
      expect(result.fieldErrors.confirmPassword).toBeDefined();
      expect(result.fieldErrors.first_name).toBeDefined();
      expect(result.fieldErrors.last_name).toBeDefined();
      expect(result.fieldErrors.phone).toBeDefined();
    });
  });

  describe("validateLoginForm", () => {
    it("should validate valid login form", () => {
      const validFormData = {
        email: "test@example.com",
        password: "anypassword",
      };

      const result = validateLoginForm(validFormData);
      expect(result.isValid).toBe(true);
      expect(Object.keys(result.fieldErrors)).toHaveLength(0);
    });

    it("should reject form with missing fields", () => {
      const invalidFormData = {
        email: "",
        password: "",
      };

      const result = validateLoginForm(invalidFormData);
      expect(result.isValid).toBe(false);
      expect(result.fieldErrors.email).toBeDefined();
      expect(result.fieldErrors.password).toBeDefined();
    });

    it("should reject invalid email but allow any password", () => {
      const formData = {
        email: "invalid-email",
        password: "weak", // Login doesn't validate password strength
      };

      const result = validateLoginForm(formData);
      expect(result.isValid).toBe(false);
      expect(result.fieldErrors.email).toBeDefined();
      expect(result.fieldErrors.password).toBeUndefined();
    });
  });
});
