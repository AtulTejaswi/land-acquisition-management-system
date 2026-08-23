import { useAuth } from '../store/AuthContext';

const ROLE_HIERARCHY: Record<string, number> = {
  super_admin: 6,
  state_authority: 5,
  district_officer: 4,
  agency: 3,
  field_officer: 2,
  citizen: 1,
};

export function useRoleGuard() {
  const { user } = useAuth();

  const hasRole = (roles: string[]) => {
    if (!user) return false;
    return roles.includes(user.role_name);
  };

  const hasMinRole = (minRole: string) => {
    if (!user) return false;
    const userLevel = ROLE_HIERARCHY[user.role_name] || 0;
    const minLevel = ROLE_HIERARCHY[minRole] || 0;
    return userLevel >= minLevel;
  };

  const isStateScoped = () => {
    if (!user) return false;
    return ['state_authority', 'district_officer', 'field_officer'].includes(user.role_name);
  };

  const isDistrictScoped = () => {
    if (!user) return false;
    return ['district_officer', 'field_officer'].includes(user.role_name);
  };

  const isCitizen = () => user?.role_name === 'citizen';
  const isAdmin = () => user?.role_name === 'super_admin';
  const isFieldOfficer = () => user?.role_name === 'field_officer';

  return {
    user,
    hasRole,
    hasMinRole,
    isStateScoped,
    isDistrictScoped,
    isCitizen,
    isAdmin,
    isFieldOfficer,
  };
}
