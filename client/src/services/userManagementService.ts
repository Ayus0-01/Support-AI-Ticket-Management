import api from '../api';

export interface ManagedUser {
  id: string;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string | null;
  last_login_at: string | null;
}

export interface ManagedUserDirectory {
  users: ManagedUser[];
  roles: string[];
}

export interface CreateManagedUserInput {
  username: string;
  email: string;
  mobile?: string;
  password: string;
  role: string;
}

export interface UpdateManagedUserInput {
  role?: string;
  is_active?: boolean;
}

function validateDirectory(data: unknown): ManagedUserDirectory {
  const directory = data as Partial<ManagedUserDirectory>;

  if (!Array.isArray(directory.users) || !Array.isArray(directory.roles)) {
    throw new Error('The user directory response was invalid.');
  }

  return {
    users: directory.users,
    roles: directory.roles,
  };
}

function validateManagedUser(data: unknown): ManagedUser {
  const response = data as { user?: ManagedUser };

  if (!response.user || !response.user.id) {
    throw new Error('The account response was invalid.');
  }

  return response.user;
}

export async function getManagedUsers(): Promise<ManagedUserDirectory> {
  const response = await api.get('/api/auth/admin/users/');
  return validateDirectory(response.data);
}

export async function createManagedUser(
  input: CreateManagedUserInput,
): Promise<ManagedUser> {
  const response = await api.post('/api/auth/admin/users/', input);
  return validateManagedUser(response.data);
}

export async function updateManagedUser(
  userId: string,
  updates: UpdateManagedUserInput,
): Promise<ManagedUser> {
  const response = await api.patch(`/api/auth/admin/users/${userId}/`, updates);
  return validateManagedUser(response.data);
}
