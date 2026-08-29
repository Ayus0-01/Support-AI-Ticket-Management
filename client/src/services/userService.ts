import api from "../api";

export type AdminUser = {
  id: string;
  username: string;
  email: string;
  mobile: string;
  role: "User" | "Agent" | "Admin";
  status: "Active" | "Inactive";
};

export type CreateUserBody = {
  username: string;
  email: string;
  mobile?: string;
  password?: string;
  role: "User" | "Agent" | "Admin";
  status?: "Active" | "Inactive";
};

export type UpdateUserBody = {
  role?: "User" | "Agent" | "Admin";
  status?: "Active" | "Inactive";
};

export const getUsers = async (): Promise<AdminUser[]> => {
  const response = await api.get("/api/auth/admin/users/");
  const users = response.data;

  if (!Array.isArray(users)) {
    throw new Error("Admin users response did not contain a user array.");
  }

  return users;
};

export const createUser = async (body: CreateUserBody): Promise<AdminUser> => {
  const response = await api.post("/api/auth/admin/users/", body);
  return response.data;
};

export const updateUser = async (
  userId: string,
  body: UpdateUserBody
): Promise<AdminUser> => {
  const response = await api.patch(`/api/auth/admin/users/${userId}/`, body);
  return response.data;
};
