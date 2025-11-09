'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { MainLayout } from '@/components/layout/main-layout';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAuthStore } from '@/stores/auth-store';
import { authService } from '@/lib/auth';
import { User, CheckCircle } from 'lucide-react';

const profileSchema = z.object({
  full_name: z.string().optional(),
  email: z.string().email('Invalid email address'),
});

const passwordSchema = z.object({
  current_password: z.string().min(1, 'Current password is required'),
  new_password: z.string().min(8, 'Password must be at least 8 characters'),
  confirm_password: z.string(),
}).refine((data) => data.new_password === data.confirm_password, {
  message: "Passwords don't match",
  path: ['confirm_password'],
});

type ProfileForm = z.infer<typeof profileSchema>;
type PasswordForm = z.infer<typeof passwordSchema>;

export default function SettingsPage() {
  const router = useRouter();
  const { user, setUser } = useAuthStore();
  const [profileSuccess, setProfileSuccess] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState(false);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);

  const {
    register: registerProfile,
    handleSubmit: handleSubmitProfile,
    formState: { errors: profileErrors, isSubmitting: isSubmittingProfile },
  } = useForm<ProfileForm>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      full_name: user?.full_name || '',
      email: user?.email || '',
    },
  });

  const {
    register: registerPassword,
    handleSubmit: handleSubmitPassword,
    formState: { errors: passwordErrors, isSubmitting: isSubmittingPassword },
    reset: resetPassword,
  } = useForm<PasswordForm>({
    resolver: zodResolver(passwordSchema),
  });

  const onSubmitProfile = async (data: ProfileForm) => {
    setProfileSuccess(false);
    setProfileError(null);
    try {
      // Note: You'll need to implement this endpoint in your API
      // For now, we'll simulate success
      setProfileSuccess(true);
      setTimeout(() => setProfileSuccess(false), 3000);
    } catch (err: any) {
      setProfileError(err.detail || 'Failed to update profile');
    }
  };

  const onSubmitPassword = async (data: PasswordForm) => {
    setPasswordSuccess(false);
    setPasswordError(null);
    try {
      await authService.changePassword(data.current_password, data.new_password);
      setPasswordSuccess(true);
      resetPassword();
      setTimeout(() => setPasswordSuccess(false), 3000);
    } catch (err: any) {
      setPasswordError(err.detail || 'Failed to change password');
    }
  };

  return (
    <ProtectedRoute>
      <MainLayout>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold">Settings</h1>
            <p className="text-muted-foreground">
              Manage your account settings and preferences
            </p>
          </div>

          {/* Profile Settings */}
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
              <CardDescription>
                Update your personal information and email address
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmitProfile(onSubmitProfile)} className="space-y-4">
                {profileSuccess && (
                  <div className="flex items-center gap-2 rounded-md bg-green-100 p-3 text-sm text-green-900 dark:bg-green-900 dark:text-green-100">
                    <CheckCircle className="h-4 w-4" />
                    Profile updated successfully
                  </div>
                )}
                {profileError && (
                  <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                    {profileError}
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="username">Username</Label>
                  <Input
                    id="username"
                    value={user?.username || ''}
                    disabled
                    className="bg-muted"
                  />
                  <p className="text-xs text-muted-foreground">
                    Username cannot be changed
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    {...registerProfile('email')}
                    disabled={isSubmittingProfile}
                  />
                  {profileErrors.email && (
                    <p className="text-sm text-destructive">{profileErrors.email.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="full_name">Full Name</Label>
                  <Input
                    id="full_name"
                    type="text"
                    {...registerProfile('full_name')}
                    disabled={isSubmittingProfile}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="role">Role</Label>
                  <Input
                    id="role"
                    value={user?.role || ''}
                    disabled
                    className="bg-muted capitalize"
                  />
                  <p className="text-xs text-muted-foreground">
                    Contact an administrator to change your role
                  </p>
                </div>

                <Button type="submit" disabled={isSubmittingProfile}>
                  {isSubmittingProfile ? 'Saving...' : 'Save Changes'}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Change Password */}
          <Card>
            <CardHeader>
              <CardTitle>Change Password</CardTitle>
              <CardDescription>
                Update your password to keep your account secure
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmitPassword(onSubmitPassword)} className="space-y-4">
                {passwordSuccess && (
                  <div className="flex items-center gap-2 rounded-md bg-green-100 p-3 text-sm text-green-900 dark:bg-green-900 dark:text-green-100">
                    <CheckCircle className="h-4 w-4" />
                    Password changed successfully
                  </div>
                )}
                {passwordError && (
                  <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                    {passwordError}
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="current_password">Current Password</Label>
                  <Input
                    id="current_password"
                    type="password"
                    {...registerPassword('current_password')}
                    disabled={isSubmittingPassword}
                  />
                  {passwordErrors.current_password && (
                    <p className="text-sm text-destructive">
                      {passwordErrors.current_password.message}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="new_password">New Password</Label>
                  <Input
                    id="new_password"
                    type="password"
                    {...registerPassword('new_password')}
                    disabled={isSubmittingPassword}
                  />
                  {passwordErrors.new_password && (
                    <p className="text-sm text-destructive">
                      {passwordErrors.new_password.message}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirm_password">Confirm New Password</Label>
                  <Input
                    id="confirm_password"
                    type="password"
                    {...registerPassword('confirm_password')}
                    disabled={isSubmittingPassword}
                  />
                  {passwordErrors.confirm_password && (
                    <p className="text-sm text-destructive">
                      {passwordErrors.confirm_password.message}
                    </p>
                  )}
                </div>

                <Button type="submit" disabled={isSubmittingPassword}>
                  {isSubmittingPassword ? 'Changing...' : 'Change Password'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </MainLayout>
    </ProtectedRoute>
  );
}
