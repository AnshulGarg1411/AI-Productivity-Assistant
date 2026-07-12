// import api from "./api";
import api from "./axios";
// ======================================
// GET ALL EMAILS
// ======================================

export const getEmails = async () => {

    const response = await api.get("/emails");

    return response.data;

};

// ======================================
// GET UNREAD
// ======================================

export const getUnreadEmails = async () => {

    const response = await api.get("/emails/unread");

    return response.data;

};

// ======================================
// GET IMPORTANT
// ======================================

export const getImportantEmails = async () => {

    const response = await api.get("/emails/important");

    return response.data;

};

// ======================================
// GET STARRED
// ======================================

export const getStarredEmails = async () => {

    const response = await api.get("/emails/starred");

    return response.data;

};

// ======================================
// GET ARCHIVED
// ======================================

export const getArchivedEmails = async () => {

    const response = await api.get("/emails/archived");

    return response.data;

};

// ======================================
// SEARCH
// ======================================

export const searchEmails = async (query) => {

    const response = await api.get(

        `/emails/search?q=${query}`

    );

    return response.data;

};

// ======================================
// MARK READ
// ======================================

export const markRead = async (id) => {

    const response = await api.patch(

        `/emails/${id}/read`

    );

    return response.data;

};

// ======================================
// STAR
// ======================================

export const starEmail = async (id) => {

    const response = await api.patch(

        `/emails/${id}/star`

    );

    return response.data;

};

// ======================================
// UNSTAR
// ======================================

export const unstarEmail = async (id) => {

    const response = await api.patch(

        `/emails/${id}/unstar`

    );

    return response.data;

};

// ======================================
// ARCHIVE
// ======================================

export const archiveEmail = async (id) => {

    const response = await api.patch(

        `/emails/${id}/archive`

    );

    return response.data;

};

// ======================================
// DELETE
// ======================================

export const deleteEmail = async (id) => {

    const response = await api.delete(

        `/emails/${id}`

    );

    return response.data;

};
// ======================================
// SYNC GMAIL
// ======================================

export const syncGmail = async () => {

    const response = await api.post(

        "/gmail/sync"

    );

    return response.data;

};

// ======================================
// AI: SUMMARIZE
// ======================================

export const summarizeEmail = async (id) => {

    const response = await api.post(

        `/emails/${id}/summarize`

    );

    return response.data;

};

// ======================================
// AI: SMART REPLY
// ======================================

export const generateReply = async ({ id, tone }) => {

    const response = await api.post(

        `/emails/${id}/reply`,

        { tone }

    );

    return response.data;

};